import crewai
from langchain_openai import ChatOpenAI

class StandartMessageAgency:
    def __init__(self, client_description: str):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        self.client_description = client_description

    def writer(self) -> crewai.Agent:
        return crewai.Agent(
            name="Gerador de Frases de Prospecção",
            role="Especialista em Prospecção",
            goal="Criar frases personalizadas para a primeira abordagem com leads, explicando brevemente a atuação da empresa e perguntando se o lead é o responsável por essa iniciativa.",
            backstory=(
                "Um agente especialista em prospecção, treinado para criar mensagens claras e persuasivas para atrair leads B2B. "
                "Ele entende a missão e os diferenciais de cada empresa, garantindo que a abordagem seja personalizada e eficaz."
            ),
            llm=self.llm,
            verbose=True
        )

    def generate_standart_message(self) -> crewai.Task:
        return crewai.Task(
            description=(
                "Crie uma frase de prospecção para o primeiro contato com um lead. "
                "A frase deve seguir a estrutura do exemplo abaixo:\n\n"
                "🔹 **Exemplo de frase padrão:**\n"
                "Estou animado por termos a chance de conversar.\n"
                "Aqui na Atllas, somos especialistas em recuperação de crédito e ajudamos nossos clientes a reduzir a inadimplência enquanto fortalecemos o relacionamento com eles.\n"
                "Gostaria de apresentar como podemos lhe ajudar a melhorar os resultados e aumentar a receita.\n"
                "Você é o principal responsável por esse tipo de iniciativa na empresa?\n\n"
                "Agora, gere uma frase seguindo esse modelo, mas personalizada para a empresa abaixo:\n\n"
                f"🔹 **Descrição da empresa:** {self.client_description}\n\n"
            ),
            expected_output="A frase gerada deve ser clara, persuasiva e direta, seguindo o mesmo tom e estrutura do exemplo acima.Inclua os \n para faciliar a leitura.",
            agent=self.writer()
        )
    
    def crew(self) -> crewai.Crew:
        return crewai.Crew(
            agents=[self.writer()],
            tasks=[self.generate_standart_message()]
        )