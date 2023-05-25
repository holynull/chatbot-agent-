import os
from dotenv import load_dotenv
import cmc_quotes_chain 
from langchain.chat_models import ChatOpenAI
from langchain.chains import APIChain
import all_templates
from langchain.prompts import PromptTemplate



# if getattr(sys, 'frozen', False):
#     script_location = pathlib.Path(sys.executable).parent.resolve()
# else:
#     script_location = pathlib.Path(__file__).parent.resolve()
load_dotenv(dotenv_path= '.env')

llm = ChatOpenAI(
	model="gpt-4",
    temperature=0.9,
    verbose=True,
    )
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.getenv("CMC_API_KEY"),
}
# cmc_currency_map_api=APIChain.from_llm_and_api_docs(llm=llm,api_docs=all_templates.cmc_currency_map_api_doc,headers=headers,verbose=True)
cmc_quotes_api=APIChain.from_llm_and_api_docs(llm=llm,api_docs=all_templates.cmc_quote_lastest_api_doc,headers=headers,verbose=True)
# prompt=PromptTemplate(template=all_templates.quotes_chain_template,input_variables=["user_input"])
# chain = cmc_quotes_chain.CMCQuotesChain(llm=llm,prompt=prompt,cmc_currency_map_api=cmc_currency_map_api,cmc_quotes_api=cmc_quotes_api,verbose=True) 
input=input() 
print(f"Output:{cmc_quotes_api(inputs=input)}")