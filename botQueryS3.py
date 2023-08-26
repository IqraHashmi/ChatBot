import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain import OpenAI, VectorDBQA
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.question_answering import load_qa_chain
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import boto3
import sys
import shutil


question=sys.argv[1]
email=sys.argv[2]
botName=sys.argv[3]
os.environ["OPENAI_API_KEY"] = "..............."
os.environ['AWS_ACCESS_KEY_ID'] = '............'
os.environ['AWS_SECRET_ACCESS_KEY'] = '...............'
persist_directory="/home/ubuntu/urlEmbeddings/"+email+"/"+botName
s3_key = f'{email}/Embeddings/{botName}'
s3_bucket = '.............'

#if os.path.isdir(persist_directory):
        
session = boto3.Session(
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
)
s3 = session.client('s3')

# list objects in the specified directory
response = s3.list_objects(Bucket=s3_bucket, Prefix=s3_key)


if 'Contents' in response:
        for obj in response.get('Contents', []):
                object_key = obj['Key']
                if not os.path.exists(persist_directory):
                        os.makedirs(persist_directory)

                local_file_path = os.path.join(persist_directory, object_key[len(s3_key):].lstrip('/'))

                # create the directory if it doesn't exist
                local_file_dir = os.path.dirname(local_file_path)
                os.makedirs(local_file_dir, exist_ok=True)
    
                s3.download_file(s3_bucket, object_key, local_file_path)
                
        try:
                print(persist_directory)
                embedding = OpenAIEmbeddings()
                docsearch= Chroma(persist_directory=persist_directory, embedding_function=embedding)
                llm=OpenAI(temperature=0)
                # llm = OpenAI(temperature=0, model_name='text-davinci-002')
                chain=RetrievalQAWithSourcesChain.from_llm(llm=llm,retriever=docsearch.as_retriever(search_kwargs={"k": 1}))
                answer=chain({"question":question},return_only_outputs=True)
                print(answer)
                print('answerStart'+str(answer['answer'])+'answerEnd')
                print('sourceStart'+str(answer['sources'])+'sourceEnd')
                print("----------------------QueryCompleted--------------------------")
        finally:
                # Clean up resources after operations
                shutil.rmtree(persist_directory)
else:
        print('answerStartBot not found!answerEnd')
        print('sourceStartsourceEnd')

