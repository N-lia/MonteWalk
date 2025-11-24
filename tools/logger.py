import logging
from config import LOG_FILE

# Ensure logger is configured
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuantAgentAudit")

def log_action(action_type: str, details: str) -> str:
    """
    Logs an agent action or reasoning step for audit purposes.
    
    Args:
        action_type: Category (e.g., 'REASONING', 'TRADE_DECISION', 'ERROR').
        details: Description of the action.
    """
    logger.info(f"[{action_type.upper()}] {details}")
    return "Action logged successfully."
