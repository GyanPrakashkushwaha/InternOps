
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from main import workflow


loader = PyPDFLoader(
    file_path="jd_and_resume/resume.pdf"
)
doc = loader.load()
resume_text = """"""
for page in doc:
    resume_text += page.page_content + "\n"
    
loader = TextLoader("jd_and_resume/jd.txt", encoding="utf-8")
document = loader.load()

jd = """"""
for doc in document:
    jd += doc.page_content + "\n"

initial_state = {
    "resume_text": resume_text,
    "job_description": jd
}

final_state = workflow.invoke(initial_state)
print(final_state)
print(final_state["ats_result"])
# print(final_state["recruiter_result"])

output = {
    "resume": final_state["resume_text"],
    "jd": final_state["job_description"],
    "ats_result": final_state["ats_result"].model_dump(),
    # "recruiter_result": final_state["recruiter_result"].model_dump() if final_state["recruiter_result"] else None ,
    # "hm_result": final_state["hm_result"].model_dump() if final_state["hm_result"] else None,
    # "finalStatus": final_state["final_status"] if final_state["final_status"] else None
}
print(output)