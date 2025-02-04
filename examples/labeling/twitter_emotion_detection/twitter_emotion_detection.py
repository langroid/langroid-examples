from langroid.agent import ChatDocument
from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.utils.logging import setup_colored_logging
from langroid.vector_store.qdrantdb import QdrantDBConfig
from langroid.agent.special.retriever_agent import (
    RecordDoc,
    RecordMetadata,
    RetrieverAgent,
    RetrieverAgentConfig,
)
from langroid.parsing.parser import ParsingConfig

import pandas as pd
import numpy as np
import asyncio
import time
from typing import Any, Dict, List, Sequence

from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score


# TODO: Generalize for any multi-label classification task and fetch constants from user
class TweetRetrieverAgentConfig(RetrieverAgentConfig):
    system_message: str = "You are a tweet expert!"
    user_message: str = """
        Your task is to match a tweet to a list of examples in a table based on semantic similarity between the given tweet and the examples in the table.
        """
    data: List[Dict[str, Any]]
    n_matches: int = 1  # num final matches to be picked by LLM
    vecdb: QdrantDBConfig = QdrantDBConfig(
        collection_name="tweet-emotion-detection",
        storage_path=":memory:",
    )
    parsing: ParsingConfig = ParsingConfig(
        n_similar_docs=5,
    )
    cross_encoder_reranking_model = ""  # turn off cross-encoder reranking


# TODO: Logic for get_records can come from user
class TweetRetrieverAgent(RetrieverAgent):
    def __init__(self, config: TweetRetrieverAgentConfig):
        super().__init__(config)
        self.config = config

    def get_records(self) -> Sequence[RecordDoc]:
        return [
            RecordDoc(
                content=", ".join(f"{k}={v}" for k, v in d.items()),
                metadata=RecordMetadata(id=i),
            )
            for i, d in enumerate(self.config.data)
        ]


# TODO: think about whether this can generalize to other type of labeling tasks
def convert_to_dict(sentiment):
    # If sentiment output is DO-NOT-KNOW, return empty dict
    if sentiment == 'DO-NOT-KNOW':
        return {}

    # Split the text into lines. Only applicable when batching inputs
    lines = sentiment.split('\n')

    # Initialize an empty dictionary to store the extracted information
    sentiment_dict = {}

    # Iterate through each line and extract the information
    for line in lines:
        # Split each line into two parts at ':'
        # Example line: Sentiment[1]: anger, optimism, trust
        parts = line.split(':')
        if len(parts) == 2:
            # Extract the sentiment index and sentiment content
            index = parts[0].split('[')[1].split(']')[0]
            content = parts[1].strip()
            # Add the information to the dictionary
            sentiment_dict[index] = content

    # Print the resulting dictionary
    return sentiment_dict


def compute_acc(llm_labels, gt_labels):
    return accuracy_score(gt_labels, llm_labels)


def compute_f1(llm_labels, gt_labels, all_labels):
    mlb = MultiLabelBinarizer()
    mlb.fit([all_labels])

    return f1_score(
        mlb.transform([x.split(', ') for x in gt_labels]),
        mlb.transform([x.split(', ') for x in llm_labels]),
        average='micro',
        zero_division=0,
    )


class TweetEmotionDetector:
    def __int__(
            self,
            chat_agent_config: ChatAgentConfig,
            rag_seed_file: str,
            tweet_test_file: str,
            concurrency: int,
            batch_size: int,
            batch_base_prompt: str,
            sleep_secs: int = 60
    ):
        setup_colored_logging()

        self.chat_agent_config = chat_agent_config
        self.tweet_emotion_detector_agent = ChatAgent(chat_agent_config)
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.sleep_secs = sleep_secs
        self.batch_base_prompt = batch_base_prompt

        rag_seed_data = pd.read_csv(rag_seed_file).to_dict('records')
        self.tweet_retriever_agent = TweetRetrieverAgent(TweetRetrieverAgentConfig(data=rag_seed_data))
        self.tweet_retriever_agent.ingest()

        self.test_df = pd.read_csv(tweet_test_file)
        self.test_df['ID'] = range(1, len(self.test_df) + 1)

        self.results_file = "./test_llm_responses.csv"
        self.results = {}

        # TODO: for debug purposes only, must be removed
        self.test_df = self.test_df[self.test_df['ID'] < 15]
        self.llm_responses = None

    # TODO: Implement non-batched version
    def run_tweet_emotion_detect(self):
        pass

    def run_tweet_emotion_detect_async_batch(self):
        async def _run_task(msg: str):
            agent = ChatAgent(self.chat_agent_config)
            task_output = None
            task_output = await agent.llm_response_forget_async(msg)
            return task_output

        async def _run_all(prompts):
            return await asyncio.gather(*(_run_task(prompt) for prompt in prompts))

        chunk_size = self.batch_size * self.concurrency
        total_chunks = len(self.test_df) // chunk_size + (len(self.test_df) % chunk_size > 0)

        result = []
        for chunk_no in range(total_chunks):
            chunk_start_idx = chunk_no * chunk_size
            chunk_end_idx = (chunk_no + 1) * chunk_size
            chunk = self.test_df.iloc[chunk_start_idx:chunk_end_idx]

            batches = np.array_split(chunk, self.concurrency)

            prompts: List[str] = []
            for batch in batches:
                prompt = []
                few_shot_examples = []
                for index, row in batch.iterrows():
                    # format prompt
                    formatted_str = f"Tweet[{row['ID']}]: {row['example']}"
                    prompt.append(formatted_str)

                    # fetch the nearest example using RAG
                    nearest_example = self.tweet_retriever_agent.get_relevant_chunks(query=row['example'])[0].content
                    tweet = nearest_example.split("example=")[1].split(", labels=")[0]
                    labels = nearest_example.split(", labels=")[1]

                    few_shot_examples.append((tweet, labels))

                few_shot_prompt = self.batch_base_prompt
                for idx in range(len(few_shot_examples)):
                    formatted_str = f"Tweet[{idx + 1}]: {few_shot_examples[idx][0]}"
                    few_shot_prompt = few_shot_prompt + formatted_str + "\n"
                for idx in range(len(few_shot_examples)):
                    formatted_str = f"Sentiment[{idx + 1}]: {few_shot_examples[idx][1]}"
                    few_shot_prompt = few_shot_prompt + formatted_str + "\n"
                few_shot_prompt = few_shot_prompt + "\n"

                prompts.append(few_shot_prompt + '\n'.join(prompt) + '\n')

            sentiments = asyncio.run(_run_all(prompts))

            time.sleep(self.sleep_secs)

            result.append(sentiments)

        self.llm_responses = self.process_llm_responses(result)

        self.compute_results(self.llm_responses)

    def process_llm_responses(self, llm_responses: List[List[ChatDocument]]):
        llm_responses_dict = {}
        for llm_response_batch in llm_responses:
            for llm_response in llm_response_batch:
                llm_responses_dict.update(convert_to_dict(llm_response.content))
        llm_responses_dict_list = [{'ID': int(key), 'Sentiment': value} for key, value in llm_responses_dict.items()]
        llm_responses_df = pd.DataFrame(llm_responses_dict_list)
        llm_responses_df.to_csv(self.results_file, index=False)
        return llm_responses_df

    def compute_results(self, llm_responses):
        combined_labels_df = self.test_df.merge(llm_responses, on="ID", how="inner")
        all_labels = list(set(combined_labels_df['labels'].str.cat(sep=', ').split(', ')))
        self.results['Accuracy'] = compute_acc(combined_labels_df['Sentiment'], combined_labels_df['labels'])
        self.results['F1'] = compute_f1(combined_labels_df['Sentiment'], combined_labels_df['labels'], all_labels)
