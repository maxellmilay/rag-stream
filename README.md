# Chatbot with RAG using Streamlit Journal

Creating RAG applications is quite simple if you think of its basic architecture. All you need to have is a vector database, a large language model, and some embedding function. The learning curve then typically happens when a RAG chatbot is being integrated into a system, either a large codebase, or a some feature that needs a chatbot, where custom functionalities are needed. For me, I encountered a quite unorthodox problem, where the framework that was given to me lacks the capacity to handle the complex functionlities in my head.

This is the first time that I had developed using Streamlit. Moreover, this is the first time that I had created an LLM based application where the backend is not separated with the frontend. I am used to developing large scale applications, where in my previous projects and occupation, I always had to think in the big picture, like how to create UIs and APIs such that it can be easily be built upon in the future. While I was using Steamlit, I cannot envision a large scale project using the framework itself. Maybe it's because I do not have enough experience with it, and if that is the case, I am more than willing to be proven wrong.

Streamlit is really wierd since the code to render the UI in the browser is integrated in the main code itself. I feel like developing with express or flask, but in this case, I am coding the UI in the server. I also tried replicating the concept of components like in most frontend frameworks like React, but I had no time to refactor the 

## Architecture

### Storing Knowledge Base Embeddings

<p>
  <img src="./documentation/images/store-embeddings.png"/>
</p>

I initially planned to create different conversations 

### Generating LLM Completion

<p>
  <img src="./documentation/images/generate-completion.png"/>
</p>

## Deployment