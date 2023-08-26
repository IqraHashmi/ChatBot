import os
from langchain.document_loaders import S3FileLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain import OpenAI, VectorDBQA
from langchain.document_loaders import UnstructuredURLLoader
from langchain import OpenAI
from langchain.text_splitter import CharacterTextSplitter
import boto3
import shutil
import sys

urlsStr=sys.argv[1]
email=sys.argv[2]
botName=sys.argv[3]
manualText=sys.argv[4]
s3Doc=sys.argv[5]
charLimit=int(sys.argv[6])
persist_directory="/home/ubuntu/urlEmbeddings/"+email+"/"+botName
os.environ["OPENAI_API_KEY"] = "......."
os.environ['AWS_ACCESS_KEY_ID'] = '..........'
os.environ['AWS_SECRET_ACCESS_KEY'] = '..................'
s3_key_prefix = f'{email}/Embeddings/{botName}'
s3_bucket = '...........'
print(persist_directory)


text_splitter = CharacterTextSplitter(separator='\n',
                                      chunk_size=1000,
                                      chunk_overlap=200)
urlsData=[]
if len(urlsStr) != 0:
    urlsArr = urlsStr.split(",")
    urls =urlsArr

    loaders = UnstructuredURLLoader(urls=urls)
    data = loaders.load()
    urlsData = text_splitter.split_documents(data)

manualData=[]
if len(manualText) != 0:
    metadatas = [{'source': 'Free_text'}]
    tx = text_splitter.create_documents([manualText], metadatas=metadatas)
    manualData = text_splitter.split_documents(tx)

docData=[]
if len(s3Doc) != 0:
    docArr = s3Doc.split(",")
    for doc in docArr:
        try:
                loader1 = S3FileLoader(s3_bucket, doc)
                loadedData = loader1.load()
                docData = docData+text_splitter.split_documents(loadedData)
        except:
                docData=docData+[]
                print(doc)
docs=urlsData+manualData+docData
text=""
for i in range(len(docs)):
    if hasattr(docs[i], 'page_content') and docs[i].page_content:
            text = text + docs[i].page_content[:]
    else:
            text = text+str(docs[i])

            
char_count = len(text)
if char_count <= charLimit:
    embeddings = OpenAIEmbeddings()
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)
    try:
        docsearch = Chroma.from_documents(documents=docs, embedding=embeddings,persist_directory=persist_directory)
        docsearch.persist()
        session = boto3.Session(
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        s3 = session.client('s3')

        def delete_all_objects_in_prefix(bucket, prefix):
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

            for obj in response.get('Contents', []):
                s3.delete_object(Bucket=bucket, Key=obj['Key'])
                print(f"Deleted object {obj['Key']} from S3")

        def upload_directory_contents(local_dir, s3_key_prefix):
            sub_dir=os.path.join(s3_key_prefix, "index")
            # Check if object exists before deleting
            if remove_s3_directory(s3_bucket, sub_dir):
                print(sub_dir)
                s3.delete_object(Bucket=s3_bucket, Key=sub_dir)

            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, persist_directory)
                    s3_key = os.path.join(s3_key_prefix, relative_path)
                    
                    
                    # Upload the file to S3
                    s3.upload_file(local_file_path, s3_bucket, s3_key)

                # Upload the files in the top-level directory itself
                if root == local_dir:
                    for file in files:
                        local_file_path = os.path.join(root, file)
                        s3_key = os.path.join(s3_key_prefix, file)
                        
                        # Upload the file to S3
                        s3.upload_file(local_file_path, s3_bucket, s3_key)

        def remove_s3_directory(s3_bucket, directory_key):
            # List objects with the specified key prefix
            response = s3.list_objects(Bucket=s3_bucket, Prefix=directory_key)
            
            # Check if any objects were found
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Delete each object
                    s3.delete_object(Bucket=s3_bucket, Key=obj['Key'])
                return True
            else:
                return False


        try:
            upload_directory_contents(persist_directory, s3_key_prefix)
        finally:
            # Clean up resources after operations
            shutil.rmtree("/home/ubuntu/urlEmbeddings/"+email)
        print("startCount"+str(char_count)+"endCount")
        print("----------------------BotSaved--------------------------")
    except:
        print("startCount"+str(char_count)+"endCount")
        print("error")
else:
    print("startCount"+str(char_count)+"endCount")
    print("limitExceeds")
