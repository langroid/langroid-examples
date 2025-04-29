import time

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
from typing import Any, Dict, List, Sequence

from sklearn.metrics import accuracy_score


# TODO: Generalize for any single-label classification task and fetch constants from user
class BankingTextRetrieverAgentConfig(RetrieverAgentConfig):
    system_message: str = "You are an expert at understanding bank customer support queries."
    user_message: str = """
    Your task is to match a bank statement to a list of examples in a table based on semantic similarity between the given statement and the examples in the table.
    """
    data: List[Dict[str, Any]]
    n_matches: int = 10
    vecdb: QdrantDBConfig = QdrantDBConfig(
        collection_name="banking-classification",
        storage_path=":memory:",
    )
    parsing: ParsingConfig = ParsingConfig(
        n_similar_docs=10,
    )
    cross_encoder_reranking_model = ""  # turn off cross-encoder reranking


# TODO: Logic for get_records can come from user
class BankingTextRetrieverAgent(RetrieverAgent):
    def __init__(self, config: BankingTextRetrieverAgentConfig):
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


def compute_acc(llm_labels, gt_labels):
    return accuracy_score(gt_labels, llm_labels)


class BankingTextClassifier:
    def __int__(
            self,
            chat_agent_config: ChatAgentConfig,
            rag_seed_file: str,
            banking_test_file: str,
            base_prompt: str
    ):
        setup_colored_logging()

        self.chat_agent_config = chat_agent_config
        self.banking_classifier_agent = ChatAgent(chat_agent_config)
        self.base_prompt = base_prompt

        rag_seed_data = pd.read_csv(rag_seed_file).to_dict('records')
        self.banking_text_retriever_agent = BankingTextRetrieverAgent(BankingTextRetrieverAgentConfig(data=rag_seed_data))
        self.banking_text_retriever_agent.ingest()

        self.test_df = pd.read_csv(banking_test_file)
        self.test_df['ID'] = range(1, len(self.test_df) + 1)

        self.results_file = "./test_llm_responses.csv"
        self.results = {}

        self.llm_responses = None

    def load_checkpoint(self):
        df = pd.read_csv(self.results_file)
        return dict(zip(df['ID'], df['llm_label']))

    def checkpoint_result(self, llm_responses):
        result_dict_list = [{'ID': int(key), 'llm_label': value} for key, value in llm_responses.items()]
        result_df = pd.DataFrame(result_dict_list)
        result_df.to_csv(self.results_file, index=False)
        return result_df

    def run_tweet_emotion_detect(self):
        agent = ChatAgent(self.chat_agent_config)

        llm_responses = self.load_checkpoint()
        for idx, row in self.test_df.iterrows():
            if row['ID'] not in llm_responses.keys():
                print(f"Processing idx: {idx}")
                prompt = self.base_prompt
                # todo: Use vec db directly instead of doc chat agent
                nearest_examples = self.banking_text_retriever_agent.get_relevant_chunks(query=row['text'])
                for index in range(len(nearest_examples)):
                    example = nearest_examples[index].content
                    text = example.split("text=")[1].split(", label=")[0]
                    label = example.split(", label=")[1]
                    prompt = prompt + f"Text: {text}\n"
                    prompt = prompt + f"Label: {label}\n"
                prompt = prompt + "\n" + f"Text: {row['text']}\n Label: "
                llm_responses[row['ID']] = agent.llm_response_forget(prompt).content
                if idx % 33 == 0:
                    print(f"Checkpointing llm responses after idx: {idx}")
                    self.checkpoint_result(llm_responses)
                    # BUG: reinitialize agent. After 100 requests the process starts timeing out infinitely...
                    agent = ChatAgent(self.chat_agent_config)
                    # print(f"Sleeping for a min...")
                    # time.sleep(60)

        self.llm_responses = self.checkpoint_result(llm_responses)

        self.compute_results(self.llm_responses)

    def run_tweet_emotion_detect_async_batch(self):
        pass

    def compute_results(self, llm_responses):
        combined_labels_df = self.test_df.merge(llm_responses, on="ID", how="inner")
        self.results['Accuracy'] = compute_acc(combined_labels_df['llm_label'], combined_labels_df['label'])
