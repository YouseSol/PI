import crewai
import crewai.crew
from langchain_openai import ChatOpenAI

class IntentAnalyzerAgency:
    def __init__(self, conversation_history: str):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.conversation_history = conversation_history

    def intent_analyzer(self) -> crewai.Agent:
        return crewai.Agent(
            name="Analisador de Intenção de Reunião",
            role="Especialista em análise de intenção",
            goal="Determinar se o lead deseja ou não marcar uma reunião com base no histórico da conversa.",
            backstory=(
                "Um agente treinado para interpretar mensagens e identificar sinais de interesse na marcação de reuniões. "
                "Ele analisa respostas diretas, expressões de dúvida ou hesitação, e sugere se o próximo passo deve ser marcar um encontro."
            ),
            llm=self.llm
        )

    def analyze_intent(self) -> crewai.Task:
        return crewai.Task(
            description=(
                "Analise o seguinte histórico de conversa e determine se a lead quer ou não marcar uma reunião. "
                "Responda **exclusivamente** com 'True' se a lead demonstrar interesse e 'False' caso contrário.\n\n"
                f"🔹 **Histórico da conversa:**\n{self.conversation_history}\n\n"
                "🔹 **Critérios:**\n"
                "- Responda 'True' se a lead expressar claramente interesse em agendar uma reunião.\n"
                "- Responda 'False' se houver recusa, hesitação ou falta de compromisso explícito.\n"
                "- Não forneça explicações adicionais."
            ),
            expected_output="Exclusivamente 'True' ou 'False', sem explicações adicionais.",
            agent=self.intent_analyzer()
        )
    
    def crew(self) -> crewai.Crew:
        return crewai.Crew(
            agents=[self.intent_analyzer()],
            tasks=[self.analyze_intent()]
        )
