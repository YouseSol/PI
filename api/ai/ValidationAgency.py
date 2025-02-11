import os

import crewai

from langchain_openai import ChatOpenAI

from api.APIConfig import APIConfig

from api.domain.Lead import Lead


class ValidationAgency:

    def __init__(self, message: str, lead: Lead):
        self.lead = lead
        self.message = message

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)


    def output_format_validator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Validador de Formato de Saída",
            goal=(
                "Garantir que a mensagem de saída esteja formatada como um texto simples, sem elementos estruturados como JSON, XML, ou outros formatos aninhados. "
                "Deve corrigir apenas se detectar que a mensagem está formatada de forma inadequada. "
                "Se a mensagem já estiver em texto simples e legível, nenhuma alteração deve ser feita."
            ),
            backstory=(
                "Você é especializado em transformar mensagens formatadas incorretamente em texto simples, direto e apropriado para exibição em um chat. "
                "Seu foco é preservar o conteúdo original enquanto remove estruturas ou símbolos de formatação desnecessários."
            ),
            llm=self.llm
        )

    def placeholder_validator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Verificador de Placeholders",
            goal=(
                "Identificar e corrigir placeholders não preenchidos na mensagem, como '[nome]' ou '[produto]'. "
                "Substituí-los pelos valores corretos fornecidos pelo sistema ou, se o valor não estiver disponível ou for irrelevante, remover o placeholder mantendo a fluidez da mensagem."
                f"Nome da lead: {self.lead.first_name}."
            )
            ,
            backstory=(
                "Você é responsável por garantir que a mensagem final esteja livre de placeholders não resolvidos. "
                "Para cada placeholder encontrado, substitua pelo valor correspondente do sistema, se disponível. "
                "Caso não haja um valor adequado, remova o placeholder de forma que o texto permaneça coerente e natural."
            ),
            llm=self.llm
        )

    def name_validator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Validador de Nome",
            goal=(
                f"Validar e corrigir o nome do lead utilizado na mensagem, assegurando que corresponda exatamente ao nome registrado no sistema. "
                f"Nome registrado: {self.lead.first_name}. "
                "Alterar apenas se houver divergência clara entre o nome na mensagem e o nome registrado."
            ),
            backstory=(
                "Você é responsável por garantir que o nome do lead usado na mensagem seja idêntico ao registrado no sistema. "
                "Sua tarefa é identificar inconsistências, como erros de digitação, abreviações ou nomes incorretos, e corrigi-las preservando a estrutura geral do texto."
            ),
            llm=self.llm
        )

    def gender_validator(self) -> crewai.Agent:
        return crewai.Agent(
            role="Corretor de Gênero",
            goal=(
                f"Validar e corrigir o uso do gênero na mensagem com base no gênero inferido pelo nome da lead. "
                f"Nome da lead: {self.lead.first_name}. "
                "Corrigir apenas onde houver inconsistências claras no uso do gênero, mantendo o restante do texto inalterado."
            ),
            backstory=(
                "Você é responsável por revisar o texto para garantir que o gênero utilizado seja consistente com o gênero esperado a partir do nome do lead. "
                "Seu objetivo é preservar a naturalidade e fluidez da mensagem, corrigindo apenas referências de gênero equivocadas."
            ),
            llm=self.llm
        )

    def create_task_for_agent(self, agent: crewai.Agent, description: str, use_original_message: bool = False) -> crewai.Task:
        message_context = (
            f"Mensagem original: {self.message}\n" if use_original_message else "Recebe a mensagem ajustada pelo agente anterior.\n"
        )
        return crewai.Task(
            description=f"{description}\n{message_context}",
            expected_output=(
                "A mensagem corrigida deve refletir exclusivamente os ajustes necessários, preservando o formato, estilo e conteúdo original. "
                "Nenhuma modificação além das correções requeridas deve ser feita."
            ),
            agent=agent
        )

    def crew(self) -> crewai.Crew:
        agents = [
            self.output_format_validator(),
            self.placeholder_validator(),
            # self.name_validator(),
            # self.gender_validator(),
        ]

        tasks = [
            self.create_task_for_agent(agent, f"Tarefa para o agente: {agent.role}.", use_original_message=(i == 0))
            for i, agent in enumerate(agents)
        ]

        return crewai.Crew(
            agents=agents,
            tasks=tasks,
            process=crewai.Process.sequential,
            verbose=False,
            incremental=True,
            manager_llm=self.llm
        )
