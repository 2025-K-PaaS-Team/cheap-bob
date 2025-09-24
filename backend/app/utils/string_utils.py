from typing import List, Optional

def parse_comma_separated_string(value: str) -> Optional[List[str]]:
    """콤마로 구분된 문자열을 배열로 변환
    
    Args:
        value: 콤마로 구분된 문자열
        
    Returns:
        변환된 문자열 리스트. 빈 문자열이나 None인 경우 None 반환
    """
    if not value or not value.strip():
        return None
    return [item.strip() for item in value.split(",") if item.strip()]

def join_values(objs, attr: str) -> str | None:
    """객체 리스트에서 특정 속성을 꺼내 ,로 join"""
    if not objs:
        return None
    values = []
    for obj in objs:
        v = getattr(obj, attr, None)
        if v is None:
            continue
        if hasattr(v, "value"):  # Enum인 경우
            values.append(str(v.value))
        else:
            values.append(str(v))
    return ",".join(values)
