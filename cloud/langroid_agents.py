"""
This file defines all the langroid related classes.
"""
from random import choice
from string import ascii_lowercase

from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.task import Task
from langroid.language_models.openai_gpt import (OpenAIChatModel,
                                                 OpenAIGPTConfig)


class LangroidAgent:
    def __init__(self, agent_name, chat_model=OpenAIChatModel.GPT4):
        self.name = agent_name
        config = ChatAgentConfig(
            name=agent_name,
            llm = OpenAIGPTConfig(
                chat_model=chat_model,
            ),
            vecdb=None,
        )
        self.agent = ChatAgent(config)

    def get_response(self, prompt):
        response = self.agent.llm_response(prompt)
        if response is not None:
            return response.content

        return None

class AgentManager:
    def __init__(self):
        '''
        self.agents is a dict from agent_name and the ChatAgent object.
        self.langroid_agent is a the default chat agent.
        '''
        self.agents = {}
        self.langroid_agent = LangroidAgent('default')
        pass

    def create_agent(self, name="", model=OpenAIChatModel.GPT4):
        '''
        Creates a Langroid ChatAgent with given name and model.
        If the name param is empty, it assigns a random name.
        '''
        # Assign a random name if given empty string.
        if name == "":
            name = ''.join([choice(ascii_lowercase) for _ in range(32)])

        self.agents[name] = LangroidAgent(name, model)

        return name

    def get_agent_response(self, name, prompt):
        if name in self.agents:
            return self.agents[name].get_response(prompt)

        return self.langroid_agent.get_response(prompt)

        
        