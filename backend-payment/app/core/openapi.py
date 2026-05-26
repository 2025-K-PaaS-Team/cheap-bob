from typing import Dict, Union, List


def create_error_responses(errors: Dict[int, Union[str, List[str]]]) -> Dict:
    """FastAPI 라우터의 responses 파라미터를 위한 에러 응답 생성"""
    responses = {}

    for status_code, description in errors.items():
        if isinstance(description, list):
            examples = {}
            for msg in description:
                examples[msg.split(".")[0]] = {"value": {"detail": msg}}
            responses[status_code] = {
                "description": " / ".join(description),
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"detail": {"type": "string"}}
                        },
                        "examples": examples
                    }
                }
            }
        else:
            responses[status_code] = {
                "description": description,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {"type": "string", "example": description}
                            }
                        }
                    }
                }
            }

    return responses
