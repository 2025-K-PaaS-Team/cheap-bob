from typing import Dict, Union, List


def create_error_responses(errors: Dict[int, Union[str, List[str]]]) -> Dict:
    """
    FastAPI 라우터의 responses 파라미터를 위한 에러 응답 생성
    
    사용 예:
    @router.get(
        "/stores/{store_id}",
        responses=create_error_responses({
            404: "가게를 찾을 수 없습니다",
            403: "접근 권한이 없습니다"
        })
    )
    async def get_store(store_id: str):
        ...
    """
    responses = {}
    
    for status_code, description in errors.items():
        # 리스트인 경우 처리
        if isinstance(description, list):
            examples = {}
            for i, msg in enumerate(description):
                examples[msg.split(".")[0]] = {
                    "value": {"detail": msg}
                }
            responses[status_code] = {
                "description": " / ".join(description),
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {
                                    "type": "string"
                                }
                            }
                        },
                        "examples": examples
                    }
                }
            }
        else:
            # 단일 문자열인 경우
            responses[status_code] = {
                "description": description,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {
                                    "type": "string",
                                    "example": description
                                }
                            }
                        }
                    }
                }
            }
    
    return responses