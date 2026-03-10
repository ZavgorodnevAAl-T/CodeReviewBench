import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def parse_predictions(predictions: List[str]) -> List[List[str]]:
    parsed_predictions = []
    for prediction in predictions:
        # Handle None predictions
        if prediction is None:
            logger.warning("Found None prediction, skipping...")
            parsed_predictions.append([])
            continue

        # Convert to string if not already
        if not isinstance(prediction, str):
            prediction = str(prediction)

        # Parse structured comment pattern: Comment 1: ...
        comment_pattern = re.compile(
            r'Comment\s*\d+:\s*(.*?)(?=Comment\s*\d+:|$)',
            re.DOTALL | re.IGNORECASE
        )
        comments = comment_pattern.findall(prediction)
        comments = [comment.strip() for comment in comments if comment.strip()]
        # If no structured comments were captured, fall back to the full output
        if not comments:
            fallback = prediction.strip()
            if fallback:
                parsed_predictions.append([fallback])
            else:
                parsed_predictions.append([])
        else:
            parsed_predictions.append(comments[:10])
    return parsed_predictions