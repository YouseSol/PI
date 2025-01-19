import json

import os

import crewai

from api.APIConfig import APIConfig

from api.domain.Client import Client
from api.domain.Lead import Lead


os.environ["OPENAI_API_KEY"] = APIConfig.get("OpenAI")["ApiKey"]

class OutboundSales(object):

    def __init__(self, client: Client, lead: Lead, chat_history: list[dict]):
        self.client = client
        self.lead = lead
        self.chat_history = chat_history

    def lead_explorator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Lead Explorator",
            goal="Dar dicas de como lidar com o lead observando o perfil dele.",
            backstory="Você recebe pesquisar detalhes do lead que podem ser interessantes na prospecção."
                      "Também deve determinar se o lead é propenso a comprar o produto da empresa ou não."
                      f"Primeiro nome: {self.lead.first_name}",
        )

    def behaviourist(self) -> crewai.Agent:
        return crewai.Agent(
            role="Comportamentalista",
            goal="Comportamentalista experiente capaz de identificar o momento que o lead se encontra no momento da interação.",
            backstory="Você deve identificar de o lead está interessado, se não é o momento para ele, se ele já possui o produto/serviço, "
                      "se quer saber mais ou se já é cliente.",
        )

    def psychologist(self) -> crewai.Agent:
        return crewai.Agent(
            role="Psicólogo",
            goal="Psicólogo experiente em gatilhos mentais responsável por identificar os estados de emoção do cliente e utilizá-los para convercimento.",
            backstory="Você deve determinar qual gatilho mental deve ser usado na resposta. Gatilhos mentais como escasses, reciprocidade, "
                    "autoridade, exclusividade, e entre outros.",
        )

    def communicator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Comunicador",
            goal="Comunicador experiente responsável por escrever a mensagem que será enviada para o cliente.",
            backstory="Você deve utilizar estratégias de comunicação e as análises dos outros agentes para escrever a "
                    "mensagem que será enviada ao cliente. Você tem a disposição um agente especializado em "
                    "psicologia da comunicação, um agente capaz de explorar o perfil do lead, um agente capaz "
                    "de classificar o estágio que o lead está e um especializado nos dados da empresa.",
        )

    def product_owner(self) -> crewai.Agent:
        return crewai.Agent(
            role= "Dono do Produto",
            goal= "Conhecedor do produto e dos serviços que serão oferecidos ao potencial cliente.",
            backstory="",
        )

    def task_one(self) -> crewai.Task:
        return crewai.Task(
            description="Collect recent market data and identify trends.",
            expected_output="A report summarizing key trends in the market.",
            agent=self.lead_explorator()
        )

    def crew(self) -> crewai.Crew:
        return crewai.Crew(
            agents=[
                self.lead_explorator(),
                self.behaviourist(),
                self.psychologist(),
                self.communicator(),
                self.product_owner()
            ],
            tasks=[ self.task_one() ],
            process=crewai.Process.sequential,
            verbose=True
        )
