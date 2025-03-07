from api.domain.ChatAction import ChatStatus, ChatAction

from api.domain.Client import SystemClient
from api.domain.Lead import SystemLead

from api.ai.IntentAnalyzerAgency import IntentAnalyzerAgency
from api.ai.OutboundSalesAgency import OutboundSalesAgency
from api.ai.ValidationAgency import ValidationAgency


def answer(client: SystemClient, lead: SystemLead, chat_history: list[dict]) -> ChatAction:
    
    intent_analyzer_crew = IntentAnalyzerAgency(conversation_history=chat_history).crew()
    intent_analyzer_output = intent_analyzer_crew.kickoff().raw
    
    if intent_analyzer_output == "True":
        return ChatAction(status = ChatStatus.WANT_TO_SCHEDULE_MEETING, should_answer=False)

    outbound_sales_crew = OutboundSalesAgency(client=client, lead=lead, chat_history=chat_history).crew()
    outbound_sales_output = outbound_sales_crew.kickoff().raw

    validation_crew = ValidationAgency(message=outbound_sales_output, lead=lead).crew()
    validation_output = validation_crew.kickoff().raw
    
    return ChatAction(should_answer=True, message=validation_output)