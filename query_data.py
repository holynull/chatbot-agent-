"""Create a ChatVectorDBChain for question/answering."""
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.memory import ConversationBufferMemory 
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.base import VectorStore
from langchain.utilities import GoogleSerperAPIWrapper
import os
from langchain.agents import Tool
from langchain.agents import initialize_agent,AgentType,AgentExecutor
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.question_answering import load_qa_chain
from langchain.agents.conversational_chat.base import ConversationalChatAgent

def get_qa_chain(
    chain_type: str, vectorstore: VectorStore
) -> ConversationalRetrievalChain:
    """Create a ChatVectorDBChain for question/answering."""
    # Construct a ChatVectorDBChain with a streaming llm for combine docs
    # and a separate, non-streaming llm for question generation
    question_gen_llm = ChatOpenAI(
        temperature=0,
        verbose=True,
    )
    streaming_llm = ChatOpenAI(
        streaming=True,
        verbose=True,
        temperature=0,
    )

    question_generator = LLMChain(
        llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT,  verbose=True,
    )
    doc_chain = load_qa_chain(
        streaming_llm, chain_type=chain_type,   verbose=True,
    )
    # memory = ConversationBufferMemory(
    #     memory_key='chat_history', return_messages=True, output_key='answer')
    # memory.chat_memory.add_ai_message("I'm the CMO of SWFT Blockchain and Metapath. What can I help you?")
    qa = ConversationalRetrievalChain(         # <==CHANGE  ConversationalRetrievalChain instead of ChatVectorDBChain
        # vectorstore=vectorstore,             # <== REMOVE THIS
        retriever=vectorstore.as_retriever(),  # <== ADD THIS
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        verbose=True,
        # memory=memory,
        # max_tokens_limit=4096,
    )
    return qa

def get_agent(
    chain_type: str, vcs_swft: VectorStore,vcs_path: VectorStore, agent_cb_handler) -> AgentExecutor:
    agent_cb_manager = AsyncCallbackManager([agent_cb_handler])
    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0,
        verbose=True,
        # request_timeout=120,
    )
    llm_qa = ChatOpenAI(
        temperature=0,
        verbose=True,
        # request_timeout=120,
    ) 
    search = GoogleSerperAPIWrapper()
    doc_search_swft = RetrievalQA.from_chain_type(llm=llm_qa, chain_type=chain_type, retriever=vcs_swft.as_retriever())
    doc_search_path = RetrievalQA.from_chain_type(llm=llm_qa, chain_type=chain_type, retriever=vcs_path.as_retriever())
    # doc_search = get_qa_chain(chain_type=chain_type,vectorstore=vectorstore) 
    # zapier = ZapierNLAWrapper()
    # toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
    tools = [
        Tool(
            name = "QA SWFT System",
            func=doc_search_swft.run,
            description="useful for when you need to answer questions about swft. Input should be a fully formed question.",
            coroutine=doc_search_swft.arun
        ),
         Tool(
            name = "QA Metapath System",
            func=doc_search_path.run,
            description="useful for when you need to answer questions about metapath. Input should be a fully formed question.",
            coroutine=doc_search_path.arun
        ),
        Tool(
            name = "Current Search",
            func=search.run,
            description="""
            useful for when you need to answer questions about current events or the current state of the world or you need to ask with search. 
            the input to this should be a single search term.
            """,
            coroutine=search.arun
        ),
    ]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    PREFIX = """Assistant is a large language model trained by SWFT Blockchain and Metapath. You are the CMO and CEO of SWFT and Metappath. You should answer user's questions as CMO and CEO role in the user's orginal language.

    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

    Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    And assistant as the CMO of SWFT and Metapath.
    If user ask question in some language, assistant must answer the question in that language finally.
    """ 
    SYSTEM_MESSAGE_PREFIX = """Answer the following questions as best you can. Remember you should answer the question use the language of the original input question. You have access to the following tools:"""
    agent_excutor = initialize_agent(
        tools=tools,
        llm=llm, 
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True, memory=memory,
        callback_manager=agent_cb_manager,
        # system_message=PREFIX,
        human_message="I want you answer user's question as you are CEO and CMO of SWFT and Metapath, and in the original language.",
        # prefix=PREFIX,
        # suffix=suffix,
        #system_message_prefix = SYSTEM_MESSAGE_PREFIX,
    )
    # agent=ConversationalChatAgent.from_llm_and_tools(
    #     llm=llm,
    #     tools=tools,
    #     agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, 
    #     system_message="你是swft和metapath的CMO。",
    #     human_message="我是swft和metapath的用户",
    #     )
    # agent_excutor=AgentExecutor.from_agent_and_tools(
    #     agent=agent,
    #     tools=tools,
    #     callback_manager=agent_cb_manager,
    #     memory=memory,
    #     verbose=True,
    # )
    return agent_excutor
