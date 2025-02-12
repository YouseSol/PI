import os

import crewai

from langchain_openai import ChatOpenAI

from api.domain.Client import Client
from api.domain.Lead import Lead


class OutboundSalesAgency(object):

    def __init__(self, client: Client, lead: Lead, chat_history: list[dict]):
        self.client = client
        self.lead = lead
        self.chat_history = chat_history
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
        self.manager_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

    def lead_explorator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Lead Explorator",
            goal="Dar dicas de como lidar com o lead observando o perfil dele.",
            backstory="Você recebe pesquisar detalhes do lead que podem ser interessantes na prospecção."
                      "Também deve determinar se o lead é propenso a comprar o produto da empresa ou não."
                      f"Primeiro nome: {self.lead.first_name}",
            llm=self.llm
        )

    def behaviourist(self) -> crewai.Agent:
        return crewai.Agent(
            role="Comportamentalista",
            goal="Comportamentalista experiente capaz de identificar o momento que o lead se encontra no momento da interação.",
            backstory="Você deve identificar de o lead está interessado, se não é o momento para ele, se ele já possui o produto/serviço, "
                      "se quer saber mais ou se já é cliente.",
            llm=self.llm,
            max_tokens=25000
        )

    def psychologist(self) -> crewai.Agent:
        return crewai.Agent(
            role="Psicólogo",
            goal="Psicólogo experiente em gatilhos mentais responsável por identificar os estados de emoção do cliente e utilizá-los para convercimento.",
            backstory="Você deve determinar qual gatilho mental deve ser usado na resposta. Gatilhos mentais como escasses, reciprocidade, "
                    "autoridade, exclusividade, e entre outros.",
            llm=self.llm
        )

    def communicator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Comunicador",
            goal="Comunicador experiente responsável por escrever a mensagem que será enviada para o cliente.",
            backstory="Você deve utilizar estratégias de comunicação e as análises dos outros agentes para escrever a "
                    "mensagem que será enviada ao cliente. Você tem a disposição um agente especializado em "
                    "psicologia da comunicação, um agente capaz de explorar o perfil do lead, um agente capaz "
                    "de classificar o estágio que o lead está e um especializado nos dados da empresa."
                    "- A mensagem deve ser uma resposta adequada a ultima mensagem do lead"
                    "- **Não inclua** rodapes, termos formais ou técnicos.\n"
                    "- **Não inclua** nenhum termo de template ou placeholder.\n"
                    "- A mensagem deve ser sempre em portugues"
                    "- Não repita cumprimentos, como bom dia, boa tarde, boa noite, ola, oi, tudo bem.\n"
                    "- Nunca faça ofertas que não possua os dados.\n",
            llm=self.manager_llm,
            allow_delegation=True
        )

    def product_owner(self) -> crewai.Agent:
        return crewai.Agent(
            role= "Dono do Produto",
            goal= "Conhecedor do produto e dos serviços que serão oferecidos ao potencial cliente.",
            backstory="Possui a frase padrão que será utilizada para iniciar a conversa com o lead."
                       f"Mensagem padrão: '{self.client.standard_message}'",
            llm=self.llm
        )

    def prospectar_lead(self) -> crewai.Task:
        return crewai.Task(
            description=(
                "Elaborar uma mensagem estratégica que responda a ultima mensagem do lead no historico de conversas. para engajar o lead e instigá-lo a marcar uma reunião ou passar um contato."
                "1. Se for o primeiro contato com o lead, utilize a mensagem padrão fornecida pelo Product Owner, não altere a mensagem, antes da mensagem padrão responda de maneira objetiva e curta a ultima mensagem do lead:\n"
                f"   '{self.client.standard_message}'\n\n"
                "2. Se não for o primeiro contato:\n"
                "   - Analise as mensagens anteriores e as informações fornecidas pelos outros agentes:\n"
                "       a. Lead Explorator: Informações sobre o perfil do lead e sua propensão a comprar.\n"
                "       b. Behaviourist: Momento de interesse ou estágio em que o lead se encontra (sem interesse, não é o momento, já tem o serviço, quer saber mais, já é cliente).\n"
                "       c. Psychologist: Gatilhos mentais que podem ser utilizados (escassez, exclusividade, reciprocidade, autoridade, etc.).\n"
                "   - Redija uma mensagem personalizada com o objetivo de instigar o lead, tocando em suas dores e necessidades.\n"
                "   - Caso o lead tenha objeções, mostre como a solução da empresa pode ser relevante para ele.\n\n"
                "3. Caso o lead não demonstre interesse após duas mensagens consecutivas, ou se não for qualificado, encerre a interação de forma educada, agradecendo pelo tempo.\n\n"
                "4. Caso o lead indique um outro contato:\n"
                "   - Agradeça pela indicação de forma educada e profissional.\n"
                "   - Solicite o contato do novo lead email, telefone, caso ainda não tenha recebido.\n"
                "**Regras importantes:**\n"
                "- A mensagem deve ser uma resposta adequada a ultima mensagem do lead"
                "- **Não inclua** rodapes, termos formais ou técnicos.\n"
                "- **Não inclua** nenhum termo de template ou placeholder.\n"
                "- A mensagem deve ser sempre em portugues"
                "- Mantenha uma linguagem humanizada, clara e sem sinais de que a mensagem foi automatizada.\n"
                "- Nunca pressione o lead ou prejudique o relacionamento.\n"
                "- Conduza a interação de forma estratégica e profissional."
                f"Historico de conversas: {self.chat_history}"
            ),
            expected_output=(
                "Uma mensagem humanizada e estratégica que gere engajamento, aumente a probabilidade de marcar uma reunião ou obter o contato de um responsável. "
                "A mensagem deve respeitar as diretrizes de abordagem da agência, ajustando-se ao estágio do lead, e ser capaz de encerrar a interação de forma educada caso o lead "
                "não demonstre interesse ou não seja qualificado. No caso de indicação de um novo contato, deve incluir uma abordagem que mencione a recomendação e introduza a empresa de forma clara."
            ),
            agent=self.communicator()
        )

    def crew(self) -> crewai.Crew:
        return crewai.Crew(
            agents=[
                self.communicator(),
                self.lead_explorator(),
                self.behaviourist(),
                self.psychologist(),
                self.product_owner()
            ],
            tasks=[ self.prospectar_lead() ],
            process=crewai.Process.hierarchical,
            verbose=False,
            manager_agent=self.communicator()
        )
