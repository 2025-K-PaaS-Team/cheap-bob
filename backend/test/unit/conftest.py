"""단위 테스트 부트스트랩.

env 기본값은 ``backend/test/conftest.py`` 가 미리 채워준다. 본 모듈은 SQLAlchemy 매퍼 등록만
담당한다.

SQLAlchemy 의 relationship() 는 클래스 이름 문자열 (예: ``relationship("CustomerDetail")``)
을 받으며 *모든* 매퍼가 import 된 후에야 해석된다. ``app.database.model`` barrel 을 미리
import 해 ``Base.metadata`` 와 매퍼 구성 양쪽을 확정시킨다.
"""
import app.database.model  # noqa: F401 — Base.metadata 채우기
