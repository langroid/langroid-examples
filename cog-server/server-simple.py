import langroid as lr
import langroid.language_models as lm

class Server:
    def setup(self) -> None:
        """Set up any required state or preprocessing for more efficient start"""

        self.file = None
        llm_config = lm.OpenAIGPTConfig(
            chat_model=lm.OpenAIChatModel.GPT4_TURBO,
            chat_context_length=32_000,  # set this based on model
            max_output_tokens=100,
            temperature=0.2,
            stream=True,
            timeout=45,
        )

        agent = lr.ChatAgent(
            lr.ChatAgentConfig(
                llm=llm_config
            )
        )

        self.agent = agent


    # function that will be used to serve the API calls
    def serve(
        self,
        query: str = Input(description="Query to run"),
        file: Path = Input(description="File to extract from"),
    ) -> str:
        """Extract requirements"""

        # count how many lines in file
        with open(file, "r") as f:
            lines = f.readlines()
            n_lines = len(lines)

        response = self.agent.llm_response(query)
        return f"""
        {n_lines}
        {response.content}
        """
