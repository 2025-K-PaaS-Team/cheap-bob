import { useNavigate } from "react-router-dom";

const TermsOfService = () => {
  const navigate = useNavigate();

  return (
    <div className="relative h-full py-6 text-custom-black">
      <img
        src="/icon/cross.svg"
        alt="crossIcon"
        onClick={() => navigate(-1)}
        className="absolute top-10 right-10 cursor-pointer z-10"
        width="20"
      />
      <div className="m-[20px] prose max-w-none prose-p:leading-relaxed prose-li:leading-relaxed">
        <h1 className="text-2xl font-bold mb-4">[저렴한끼] 서비스 이용약관</h1>

        <h2 className="text-xl font-semibold mt-6">서비스 이용약관</h2>
        <hr className="my-4" />

        <h2 className="text-xl font-semibold mt-8">제1장. 총칙</h2>

        <section>
          <h3 className="font-semibold mt-4">제1조 (목적)</h3>
          <p>
            1. 본 약관은 [저렴한끼]이 운영하는 모바일 애플리케이션
            ’저렴한끼’에서 제공하는 서비스 이용에 관한{" "}
            <strong>이용자와 회사 간의 권리, 의무 및 책임 사항</strong>을
            규정함을 목적으로 합니다.
          </p>
          <p>
            2. PC통신, 무선 등을 이용하는 전자상거래에 대해서도 그 성질에 반하지
            않는 한 본 약관을 준용합니다.
          </p>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제2조 (정의)</h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              <strong>‘회사’</strong>: [회사명]가 재화 또는 용역(랜덤팩 상품)을
              이용자에게 제공하기 위하여 설정한 가상의 영업장을 운영하는
              사업자를 말합니다.
            </li>
            <li>
              <strong>‘이용자’</strong>: ‘회사’의 ‘서비스’에 접속하여 회원가입을
              완료하고 본 약관에 따라 서비스를 이용하는 자를 말하며,{" "}
              <strong>회원과 동일한 의미</strong>로 사용합니다.
            </li>
            <li>
              <strong>‘랜덤팩’</strong>: ‘서비스’를 통해 판매되는 마감 할인
              상품으로,{" "}
              <strong>
                판매자가 정한 가격에 랜덤하게 구성되어 판매되는 묶음 상품
              </strong>
              을 말합니다.
            </li>
            <li>
              <strong>‘판매자’</strong>: ‘서비스’에 등록하여 샐러드, 포케 등
              마감 상품을 ‘구매자’에게 판매하는 소상공인을 말합니다. (현재
              관악구 지역에 한정됨)
            </li>
            <li>
              <strong>‘영양 목표’</strong>: 이용자가 ‘서비스’를 이용하며
              설정하는 건강 및 식단 목표로,{" "}
              <strong>최대 3개까지 선택 가능</strong>하며, ‘회사’가 ‘랜덤팩’
              상품을 추천하고 홈 화면에서 <strong>필터링하기 위한 기준</strong>
              으로 활용되는 정보 일체입니다. 영양 목표의 세부 항목과 정의는
              다음과 같습니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  <strong>다이어트</strong>: 체지방 감소와 활력 증진
                </li>
                <li>
                  <strong>저탄고지</strong>: 식곤증 없는 안정적 에너지
                </li>
                <li>
                  <strong>단백질 보충</strong>: 근육 성장과 체력 강화
                </li>
                <li>
                  <strong>저당저염</strong>: 만성질환 예방과 저속노화
                </li>
                <li>
                  <strong>균형잡힌</strong>: 영양 충전으로 활기차게
                </li>
                <li>
                  <strong>채식 위주</strong>: 심장 건강 개선과 체중 감량
                </li>
              </ul>
            </li>
            <li>
              <strong>‘선호 메뉴’</strong>: 이용자가 ‘서비스’에서 상시 선택 또는
              수정할 수 있는 메뉴 타입(샐러드, 포케, 도시락, 샌드위치 등)에 대한
              선호 정보입니다. <strong>선택 개수 제한이 없으며</strong>, 주문 시{" "}
              <strong>판매자의 참고 사항</strong>으로만 제공됩니다.
            </li>
            <li>
              <strong>‘선호 토핑’</strong>: 이용자가 상시 선택 또는 수정할 수
              있는 토핑에 대한 선호 정보입니다.{" "}
              <strong>판매자에게 참고 사항으로만 제공</strong>됩니다.
            </li>
            <li>
              <strong>‘못 먹는 음식 (제약 조건)’</strong>: 이용자가 알레르기
              또는 기피 등의 이유로 섭취를 원하지 않는 식재료 정보입니다.{" "}
              <strong>판매자에게 참고 사항으로만 제공</strong>됩니다.
            </li>
            <li>
              <strong>‘주문 확인중’</strong>: 구매자가 ‘랜덤팩’ 구매를 신청하고
              결제를 완료한 후, ‘판매자’가 해당 주문을 수락(확정)하기를{" "}
              <strong>기다리는 주문 처리 상태</strong>를 말합니다. 해당 상태에서
              구매자 및 판매자 양측 모두 주문에 대해 취소할 수 있습니다. 단,
              판매자가 주문을 취소할 시 취소 사유를 선택해야만 합니다.
            </li>
            <li>
              <strong>‘픽업 확정’</strong>: ‘판매자’가 ‘주문 확인중’인 주문을
              수락하여, 해당 주문에 대한{" "}
              <strong>
                거래 체결이 완료되었고 픽업 시간에 상품 픽업이 가능함을
                구매자에게 알리는 상태
              </strong>
              를 말합니다.
            </li>
            <li>
              <strong>‘픽업 시간’</strong>: ‘판매자’가 운영 효율화를 위해
              설정한,{" "}
              <strong>
                구매자가 매장에 방문하여 상품을 수령할 수 있는 시작 시각과 ‘픽업
                마감 시간’ 사이의 특정 기간
              </strong>
              을 말하며, 구매자는 이 시간에만 픽업이 가능합니다.
            </li>
            <li>
              <strong>‘픽업 마감 시간’</strong>: ‘판매자’가 설정한{" "}
              <strong>‘픽업 시간’의 최종 마감 시각</strong>을 말하며, 이
              시간까지 픽업되지 않은 패키지는 폐기되며 구매자에게 환불되지
              않습니다.
            </li>
            <li>
              <strong>‘주문 알림’</strong>: 이용자가 ‘랜덤팩’을 구매한 후, 해당
              주문의 <strong>실시간 상태 변화</strong>(주문 접수, 픽업 확정,
              픽업 요청, 취소 등)를 서비스 내 알림 영역을 통해 이용자에게
              통지하는 수단 또는 그 정보를 말합니다. 주요 알림 상태는 다음과
              같습니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  <strong>주문이 들어갔어요!</strong>: ‘주문 확인중’ 상태임을
                  알립니다.
                </li>
                <li>
                  <strong>픽업이 확정되었어요!</strong>: ‘픽업 확정’ 상태임을
                  알립니다.
                </li>
                <li>
                  <strong>지금 픽업해주세요!</strong>: ‘픽업 확정’ 후, ‘픽업
                  시간’이 시작되어 상품 수령이 가능함을 알립니다.
                </li>
                <li>
                  <strong>주문이 취소되었어요.</strong>: 가게나 구매자의 사유로
                  주문이 취소되어 환불 처리되었음을 알립니다.
                </li>
              </ul>
            </li>
            <li>
              <strong>‘QR 인증’</strong>: ‘판매자’가 ‘픽업 QR 표시’ 버튼을 눌러
              생성된,{" "}
              <strong>
                주문마다 고유한 QR 코드를 ‘구매자’가 카메라를 통해 스캔
              </strong>
              하고, 이를 통해{" "}
              <strong>
                주문자 본인 확인 및 픽업 완료가 시스템에 등록되는 인증 절차
              </strong>
              를 말합니다.
            </li>
            <li>
              <strong>패키지 잔여 수량</strong>: 현재 시점 기준으로{" "}
              <strong>당일 판매 가능한 ‘랜덤팩’의 남은 개수</strong>를 말합니다.
              이 수량이 구매자에게 실시간으로 노출되며, ‘0’이 되면 품절로
              처리됩니다.
              <div className="mt-2">
                <strong>계산식</strong>:{" "}
                <code>
                  (패키지 잔여 수량) = (판매 기본값) - (주문 수량) + (일일
                  조정값)
                </code>
              </div>
            </li>
            <li>
              <strong>판매 기본값</strong>: 판매자가{" "}
              <strong>
                하루에 판매할 것으로 예상하고 영구적으로 설정해 둔 기본 패키지
                개수
              </strong>
              를 말합니다. 이 값은 매일 영업 시작 시 잔여 수량의 초기 기준으로
              활용됩니다. 한 번 설정하면 다음 영업일의 잔여 수량 계산 시
              고정적으로 사용됩니다. 상시 수정할 수 있으며 수정 사항은
              다음날부터 반영됩니다.
            </li>
            <li>
              <strong>주문 수량</strong>:{" "}
              <strong>
                당일 영업시간 내에 구매자가 주문한 ‘랜덤팩’의 총 개수
              </strong>
              를 말하며, 이는 잔여 수량에서 실시간으로 차감되는 값입니다. 확정
              대기 중이거나, 픽업 확정되었거나, 이미 픽업이 완료된 모든 주문
              수량을 합산합니다.
            </li>
            <li>
              <strong>일일 조정값</strong>: ‘판매 기본값’을 설정했음에도{" "}
              <strong>당일의 재고 상황이 달라졌을 때</strong>, 점주가 잔여
              수량을 <strong>수동으로 증감</strong>시키기 위해 임시로 설정하는
              값입니다. 이 값은 <strong>영업 시간 내에만 조정 가능</strong>하며,
              당일 운영 종료 시 <strong>‘0’으로 자동 초기화</strong>되어 다음 날
              잔여 수량 계산에 영향을 미치지 않습니다.
              <div className="mt-2">
                예시: 판매 기본값을 5개로 설정했는데, 갑자기 재료가 부족해 2개만
                팔고 싶다면 ‘일일 조정값’을 ‘-3’으로 설정합니다.
              </div>
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제3조 (약관 외 준칙)</h3>
          <p>
            본 약관에서 정하지 아니한 사항은 관계 법령 및 ‘회사’가 정한 별도의
            세부지침에 따르며, 본 약관과 세부지침이 충돌할 경우에는 세부지침이
            우선합니다.
          </p>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제4조 (약관의 명시 및 개정)</h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              회사는 이 약관의 내용을 이용자가 쉽게 알 수 있도록 게시하며, 약관
              개정 시에는 적용일자 7일 전부터 공지합니다.{" "}
              <strong>
                이용자에게 불리한 내용으로 변경하는 경우 최소 30일 이상
                유예기간을 두고 공지
              </strong>
              합니다.
            </li>
            <li>
              ‘회사’는 ‘전자상거래 등에서의 소비자보호에 관한 법률’, ‘약관의
              규제에 관한 법률: 전자거래기본법’, 정보통신망 이용촉진 등에 관한
              법률, ‘소비자보호법’ 등 관련법령에 위배되지 않는 범위내에서 본
              약관을 개정할 수 있습니다.
            </li>
            <li>
              본 약관에서 정하지 아니한 사항 및 본 약관의 해석에 관하여는
              관계법령 및 건전한 상관례에 따릅니다.
            </li>
          </ol>
        </section>

        <h2 className="text-xl font-semibold mt-8">
          제2장. 서비스 이용 및 계약
        </h2>

        <section>
          <h3 className="font-semibold mt-4">제5조 (제공하는 핵심 서비스)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              <strong>영양 목표 기반 랜덤팩 매칭 서비스</strong>: 이용자의 건강
              목표에 맞는 랜덤팩 상품을 필터링하고 추천하는 개인화된 서비스.
            </li>
            <li>
              <strong>랜덤팩에 대한 구매 및 결제 중개 서비스</strong>: 한정된
              수량의 랜덤팩에 대해 안정적인 결제 환경을 제공하고 거래를 중개하는
              서비스.
            </li>
            <li>
              <strong>거래 체결 및 픽업 중개 서비스</strong>: 구매자와 판매자가
              효율적이고 오류 없이 마감 상품을 인계(픽업)할 수 있도록 전 과정을
              중개하고 관리하는 서비스.
            </li>
            <li>기타 회사가 정하는 업무</li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제6조 (서비스의 중단 등)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              ‘회사’는 시스템 점검, 유지 보수 등 특별한 사유가 있는 경우
              서비스의 전부 또는 일부를 일시 중단할 수 있습니다.
            </li>
            <li>
              ‘회사’는 전시, 사변, 천재지변 또는 이에 준하는 국가비상사태가
              발생하거나 발생할 우려가 있는 경우, 전기통신사업법에 의한
              기간통신사업자가 전기통신서비스를 중지하는 등 부득이한 사유가
              발생한 경우 서비스의 전부 또는 일부를 제한하거나 중지할 수
              있습니다.
            </li>
            <li>
              ‘회사’가 서비스를 정지하거나 이용을 제한하는 경우 그 사유 및 기간,
              복구 예정 일시 등을 지체 없이 ‘이용자’에게 알립니다.
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제7조 (회원가입)</h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              ‘회사’가 정한 양식에 따라 ‘이용자’가 회원정보를 기입한 후 본
              약관에 동의한다는 의사표시를 함으로써 회원가입을 신청합니다.
            </li>
            <li>
              ‘회사’는 전항에 따라 회원가입을 신청한 ‘이용자’ 중 다음 각호의
              사유가 없는 한 ‘회원’으로 등록합니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  가. 가입신청자가 본 약관에 따라 회원자격을 상실한 적이 있는
                  경우, 다만, ‘회사’의 재가입 승낙을 얻은 경우에는 예외로
                  합니다.
                </li>
                <li>
                  나. 회원정보에 허위, 기재누락, 오기 등 불완전한 부분이 있는
                  경우
                </li>
                <li>
                  다. 기타 회원으로 등록하는 것이 ‘회사’의 운영에 현저한 지장을
                  초래하는 것으로 인정되는 경우
                </li>
              </ul>
            </li>
            <li>
              회원가입 시기는 ‘회사’의 가입승낙 안내가 ‘회원’에게 도달한
              시점으로 합니다.
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">
            제8조 (회원탈퇴 및 자격상실 등)
          </h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              ‘회원’은 언제든지 ‘회사’에 탈퇴를 요청할 수 있으나,{" "}
              <strong>진행 중인 주문</strong>(주문 확인중, 픽업 확정 등) 또는{" "}
              <strong>거래 대금의 정산</strong>이 필요한 경우에는{" "}
              <strong>해당 주문을 모두 취소 또는 완료</strong>해야만 탈퇴가
              가능합니다.
            </li>
            <li>
              ‘회사’는 제1항의 요청을 받은 경우, 관계 법령 및 본 약관에 따라
              필요한 조치를 완료한 후 지체 없이 탈퇴를 처리합니다.
            </li>
            <li>
              탈퇴 요청 시 계정은 즉시 비활성화되며, 회원 정보의 삭제는 회사의
              개인정보 처리방침에 따라 관리자의 확인 절차를 거쳐 처리됩니다.
            </li>
            <li>
              <strong>(삭제 유예 기간 및 복구)</strong> 회원은 탈퇴 요청으로
              인해 계정이 비활성화된 시점부터{" "}
              <strong>실제 정보 삭제 처리 전까지</strong> 재로그인을 시도할 수
              있습니다. 이 경우, 회사는 ‘계정이 삭제 처리 중’임을 알리고{" "}
              <strong>계정 복구 의사</strong>를 확인할 수 있으며, 회원이 복구를
              요청하는 경우 해당 탈퇴 요청은 철회되고 계정은 재활성화됩니다.{" "}
              <strong>
                다만, 정보 삭제 처리가 완료된 이후에는 재활성화가 불가능하며
                신규 가입이 필요합니다.
              </strong>
            </li>
            <li>
              <strong>판매자 탈퇴:</strong> 판매자 회원 탈퇴 요청 시, 탈퇴
              처리는 가게 운영 중이 아닐 때만 가능하며, 조건이 충족될 시 계정이
              즉시 비활성화 처리되며 가게 정보는 다음 가게 오픈 시간 전에
              삭제됩니다. 다만 해당 가게에 대한 과거 구매자가 주문 내역을 확인할
              수 있도록 주문 정보는 유지됩니다. 구체적인 내용은 아래와 같습니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  <strong>삭제되는 정보:</strong>{" "}
                  <strong>판매자 이름, 이메일, 전화번호, 사업자 번호</strong>
                </li>
                <li>
                  <strong>유지되는 정보:</strong>{" "}
                  <strong>주문 정보(가게 이름, 패키지 이름, 가격)</strong>는
                  유지된다.
                </li>
              </ul>
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제9조 (회원에 대한 통지)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              ‘회사’는 ‘회원’ 회원가입 시 기재한 전자우편, 이동전화번호, 주소
              등을 이용하여 ‘회원’에게 통지할 수 있습니다.
            </li>
            <li>
              ‘회사’가 불특정 다수 ‘회원’에게 통지하고자 하는 경우 1주일 이상
              ‘사이트’의 게시판에 게시함으로써 개별 통지에 갈음할 수 있습니다.
              다만 ‘회원’이 서비스를 이용함에 있어 중요한 사항에 대하여는 개별
              통지합니다.
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제10조 (구매신청)</h3>
          <p>
            이용자는 ‘랜덤팩’의 정보, 가격, 픽업 시간, 영양 태그 등 필수 정보를
            확인하고 구매를 신청하며, 상품의 특성상 청약철회 제한 사항을
            확인하고 동의해야 합니다.
          </p>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제11조 (계약의 성립)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              ‘회사’는 ‘이용자’의 결제 완료 및 ‘판매자’의 픽업 확정 통지를
              함으로써 최종 계약이 성립된 것으로 봅니다.
            </li>
            <li>
              ‘회사’가 승낙의 의사표시를 하는 경우 이용자의 구매신청에 대한 확인
              및 판매가능여부, 구매신청의 정정 및 취소 등에 관한 정보가
              포함되어야 합니다.
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">
            제12조 (결제방법 및 이용 수수료)
          </h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              ‘랜덤팩’ 대금은 외부 결제 서비스(포트원 등 PG사)를 통해 결제하며,
              입력한 결제 정보에 대한 책임은 구매자가 부담합니다.
            </li>
            <li>
              이용자는 서비스 이용 대가로 수수료 등을 지급하지 않으며,{" "}
              <strong>이용 수수료는 판매자에게 부과됩니다.</strong>
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">
            제13조 (수신확인통지, 구매신청 변경 및 취소)
          </h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              ‘회사’는 ‘구매자’가 구매신청을 한 경우 ‘구매자’에게 수신확인통지를
              합니다.
            </li>
            <li>
              수신확인통지를 받은 ‘구매자’는 의사표시의 불일치가 있는 경우
              수신확인통지를 받은 후 즉시 구매신청 내용의 변경 또는 취소를
              요청할 수 있습니다. 단, 마감 할인 상품의 특성상 가게가 픽업을
              확정하기 전까지 변경 또는 취소가 가능합니다.
            </li>
          </ol>
        </section>

        <h2 className="text-xl font-semibold mt-8">
          제3장. 픽업, 환급 및 청약철회 특례
        </h2>

        <section>
          <h3 className="font-semibold mt-4">
            제14조 (재화 등의 공급 및 픽업)
          </h3>
          <p>
            ‘랜덤팩’은 구매자가 매장을 직접 방문하여 픽업하는 방식으로 제공되며,{" "}
            <strong>
              구매자는 판매자가 정한 픽업 시간 내에 상품을 수령해야 합니다.
            </strong>
          </p>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제15조 (환급)</h3>
          <p>
            회사는 ‘랜덤팩’ 품절, 결제 대기 시간 5분 초과 등으로 상품 제공이
            불가능할 경우 지체 없이 통지하고, 대금을 받은 날부터{" "}
            <strong>3영업일 이내</strong>에 환급하거나 이에 필요한 조치를
            취합니다.
          </p>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제16조 (청약철회)</h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              <strong>(청약철회 불가 특례)</strong> ‘랜덤팩’은 유통기한이 짧은
              마감 상품이므로, 다음 각 호의 경우 구매자의 단순 변심에 의한
              청약철회 및 환불은 불가합니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>가. 픽업 확정 이후</li>
                <li>나. 픽업 가능 시간 초과(노쇼)로 인한 경우</li>
              </ul>
            </li>
            <li>
              <strong>(예외적 청약철회)</strong> 다음 각 호의 사유에 한하여
              청약철회를 요청할 수 있습니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  가. 상품에 판매자의 귀책사유로 인한 명백한 결함(오염, 부패
                  등)이 발생한 경우
                </li>
                <li>
                  나. 표시된 상품 정보(주요 식재료 등)와 실제 상품이 현저히 다를
                  경우
                </li>
              </ul>
            </li>
            <li>
              <strong>(거래 중개자의 역할 및 책임 한정)</strong> 회사는 본 조
              제2항에 따른 청약철회 사유가 발생하는 경우, 거래 대금의 환불
              조치를 신속하게 이행합니다. 다만, 상품의 품질, 위생, 표시 정보의
              진실성 등 상품 자체에 대한 최종적인 책임은 판매자에게 있으며,
              회사는 거래를 중개하는 플랫폼으로서 이에 대한 책임을 부담하지
              않습니다.
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제17조 (청약철회의 효과)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              회사의 귀책사유로 인한 환불은 <strong>3영업일 이내</strong>에
              처리됩니다.
            </li>
            <li>
              <strong>노쇼에 의한 환불 제한</strong>: 구매자가 픽업 시간을
              준수하지 않아 발생하는 환불 불가 건에 대한 책임은 전적으로
              구매자에게 있습니다.
            </li>
            <li>
              <strong>결제 오류 환불</strong>: 결제 시스템 오류(예: 5분 초과
              결제)로 주문이 미처리된 경우, 회사는{" "}
              <strong>즉시 전액 환불 조치</strong>를 취합니다.
            </li>
          </ol>
        </section>

        <h2 className="text-xl font-semibold mt-8">제4장. 의무 및 분쟁 해결</h2>

        <section>
          <h3 className="font-semibold mt-4">제18조 (개인정보보호)</h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              <strong>정보 수집 및 항목</strong>: ‘회사’는 서비스 제공 및 계약
              이행을 위해 다음의 정보를 수집합니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  <strong>회원 식별 정보</strong>: 소셜 로그인 정보를 통해
                  수집되는 <strong>이메일 주소</strong> 및 소셜 서비스{" "}
                  <strong>가입 형태(네이버, 구글)</strong>
                </li>
                <li>
                  <strong>연락처 정보</strong>: 본인 확인 및 주문 관련 알림을
                  위한 <strong>전화번호 (인증 절차 없음)</strong>
                </li>
                <li>
                  <strong>서비스 맞춤 정보</strong>: <strong>닉네임</strong>,{" "}
                  <strong>영양 목표</strong>, <strong>선호 토핑/메뉴</strong>,{" "}
                  <strong>못 먹는 음식(제약 조건)</strong>
                </li>
              </ul>
            </li>
            <li>
              <strong>이메일 활용 목적</strong>: 수집된 이메일 주소는{" "}
              <strong>
                주문 상태 통지(픽업 확정/취소), 서비스 안내, 마케팅 및 이벤트
                정보 제공
              </strong>{" "}
              목적으로 활용됩니다.
            </li>
            <li>
              <strong>전화번호 활용 목적</strong>: 수집된 전화번호는{" "}
              <strong>
                거래 이행(픽업 확정 및 긴급 상황 발생 시 가게 또는 ‘회사’에서의
                연락)
              </strong>{" "}
              목적으로 사용되며, 인증 절차의 부재로 인해 발생하는 오기재로 인한
              책임은 이용자에게 있습니다.
            </li>
            <li>
              <strong>맞춤 정보 활용 목적</strong>: 수집된 영양 목표 및 선호
              정보는 <strong>‘랜덤팩’ 추천 및 필터링</strong> 목적으로만
              활용되며, 주문 시 해당 정보가 ‘판매자’에게 익명 처리되어 제공될 수
              있습니다.
            </li>
            <li>
              <strong>보호 원칙</strong>: 본 약관에 기재된 사항 외의
              개인정보보호에 관한 사항은 ‘개인정보처리방침’에 따르며, 회사는
              관계 법령을 준수하여 개인정보를 안전하게 관리합니다.
            </li>
          </ol>

          <div className="mt-4">
            <ul className="list-disc ml-5 space-y-2">
              <li>
                <strong>정보 수집 및 항목</strong>: ‘회사’는 서비스 제공, 거래
                이행 및 매장 관리를 위해 다음의 정보를 수집합니다.
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  <li>
                    <strong>이용자 (구매자) 정보</strong>:
                    <ul className="list-disc ml-6 mt-1 space-y-1">
                      <li>
                        <strong>회원 식별 정보</strong>: 소셜 로그인 정보를 통해
                        수집되는 <strong>이메일 주소</strong> 및 소셜 서비스{" "}
                        <strong>가입 형태(네이버, 카카오, 구글 등)</strong>
                      </li>
                      <li>
                        <strong>연락처 정보</strong>: 본인 확인 및 주문 관련
                        알림을 위한 <strong>전화번호 (인증 절차 없음)</strong>
                      </li>
                      <li>
                        <strong>서비스 맞춤 정보</strong>:{" "}
                        <strong>닉네임</strong>, <strong>영양 목표</strong>,{" "}
                        <strong>선호 메뉴</strong>, <strong>선호 토핑</strong>,{" "}
                        <strong>못 먹는 음식(제약 조건)</strong>
                      </li>
                    </ul>
                  </li>
                  <li>
                    <strong>판매자 (매장) 정보</strong>:
                    <ul className="list-disc ml-6 mt-1 space-y-1">
                      <li>
                        <strong>회원 식별 정보</strong>: 소셜 로그인 정보를 통해
                        수집되는 <strong>이메일 주소</strong> 및 소셜 서비스{" "}
                        <strong>가입 형태(네이버, 카카오, 구글 등)</strong>
                      </li>
                      <li>
                        <strong>매장 공개 정보</strong>:{" "}
                        <strong>매장 이름</strong>, <strong>매장 연락처</strong>
                        , <strong>매장 주소</strong>,{" "}
                        <strong>매장 대표 이미지</strong>
                      </li>
                      <li>
                        <strong>운영 정보</strong>:{" "}
                        <strong>영업 요일 및 영업 시간</strong>,{" "}
                        <strong>픽업 시간</strong>,{" "}
                        <strong>패키지 판매 기본값</strong>
                      </li>
                      <li>
                        <strong>상품 정보</strong>: <strong>패키지 이름</strong>
                        , <strong>패키지 소개</strong>,{" "}
                        <strong>패키지의 영양 특징</strong>,{" "}
                        <strong>패키지 가격</strong>,{" "}
                        <strong>패키지 구성 원가</strong>
                      </li>
                    </ul>
                  </li>
                </ul>
              </li>

              <li>
                <strong>정보의 활용 목적 및 공개 범위</strong>:
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  <li>
                    <strong>주문/알림 활용</strong>: 수집된{" "}
                    <strong>이메일 주소</strong> 및 <strong>전화번호</strong>는{" "}
                    <strong>
                      주문 상태 통지(픽업 확정/취소), 서비스 안내 및 긴급 상황
                      발생 시 연락
                    </strong>{" "}
                    목적으로 활용됩니다.{" "}
                    <strong>
                      인증 절차의 부재로 인해 발생하는 오기재로 인한 책임은
                      이용자에게 있습니다.
                    </strong>
                  </li>
                  <li>
                    <strong>맞춤 서비스 제공</strong>: 수집된{" "}
                    <strong>영양 목표, 선호 메뉴/토핑, 못 먹는 음식</strong>{" "}
                    정보는 <strong>‘랜덤팩’ 추천 및 필터링</strong> 목적으로
                    활용되며,{" "}
                    <strong>
                      주문 시 판매자에게 참고 사항으로만 익명 처리되어 제공
                    </strong>
                    됩니다.
                  </li>
                  <li>
                    <strong>판매자 정보 공개</strong>: 제1항 나호의 수집된 정보
                    중 <strong>패키지 구성 원가를 제외한 모든 정보</strong>는{" "}
                    <strong>
                      ‘랜덤팩’ 판매 및 거래 이행을 위해 ‘이용자’에게 공개
                    </strong>
                    됩니다.
                  </li>
                </ul>
              </li>

              <li>
                <strong>보호 원칙</strong>:
                <ul className="list-disc ml-6 mt-2 space-y-1">
                  <li>
                    <strong>일반 원칙</strong>: 본 조에 명시된 사항 외의
                    개인정보보호에 관한 사항은 ‘개인정보처리방침’에 따르며,
                    회사는 관계 법령을 준수하여 개인정보를 안전하게 관리합니다.
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제19조 (‘회사’의 의무)</h3>
          <p>
            회사는 관계 법령을 준수하며, 이용자가 안전하게 서비스를 이용할 수
            있도록 개인정보 보호 시스템 및 안정적인 서비스를 제공하는 데 최선을
            다합니다.
          </p>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제20조 (이용자 및 회원의 의무)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              이용자는 회원가입 시 사실에 근거하여 정보를 작성해야 하며, 특히{" "}
              <strong>알레르기 및 기피 식재료</strong>에 대한 정보를 정확히
              선택해야 합니다.
            </li>
            <li>
              이용자는 픽업 확정된 주문을 성실히 픽업해야 하며, 노쇼 등으로
              판매자에게 손해를 입히는 행위를 하여서는 안 됩니다.
            </li>
            <li>
              ‘이용자’는 주소, 연락처, 전자우편 주소 등 회원정보가 변경된 경우
              즉시 이를 수정해야 합니다. 변경된 정보를 수정하지 않거나 수정을
              게을리하여 발생하는 책임은 ‘이용자’가 부담합니다.
            </li>
            <li>
              ‘회원’은 부여된 아이디(ID)와 비밀번호를 직접 관리해야 합니다.
            </li>
            <li>
              ‘회원’이 자신의 아이디(ID) 및 비밀번호를 도난당하거나 제3자가
              사용하고 있음을 인지한 경우에는 바로 ‘회사’에 통보하고 안내에
              따라야 합니다.
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제21조 (저작권의 귀속 및 이용)</h3>
          <ol className="list-decimal ml-5 space-y-2">
            <li>
              ‘이용자’는 ‘가게’에게 지식재산권이 있는 정보를 사전 승낙없이 복제,
              송신, 출판, 배포, 방송 기타 방법에 의하여 영리목적으로 이용하거나,
              제3자가 이용하게 하여서는 안됩니다.
            </li>
            <li>
              전항의 규정에도 불구하고 ‘회사’는 서비스의 운영, 전시, 전송, 배포,
              홍보 등의 목적으로 별도의 허락 없이 무상으로 저작권법 및 공정한
              거래관행에 합치되는 범위 내에서 다음 각호와 같이 ‘이용자’가 등록한
              저 작물을 이용할 수 있습니다.
              <ul className="list-disc ml-6 mt-2 space-y-1">
                <li>
                  가. ‘회사’가 제공하는 서비스 내에서 ‘이용자’가 작성한
                  ‘콘텐츠’의 복제, 수정, 전시, 전송, 배포 등 저작 권을 침해하지
                  않는 범위 내의 2차적 저작물 또는 편집 저작물 작성을 위한 사용,
                  다만 ‘이용자’가 해당 ‘콘텐츠’의 삭제 또는 사용중지를 요청하는
                  경우 관련법에 따라 보존해야 하는 사항을 제외하고 관련
                  ‘콘텐츠’를 모두 삭제 또는 사용 중지합니다.
                </li>
                <li>
                  나. 서비스의 운영, 홍보, 서비스 개선 및 새로운 서비스 개발을
                  위한 범위내의 사용
                </li>
                <li>
                  다. 미디어, 통신사 등을 통한 홍보목적으로 ‘콘텐츠’를 제공,
                  전시하도록 하는 등의 사용
                </li>
              </ul>
            </li>
          </ol>
        </section>

        <section>
          <h3 className="font-semibold mt-4">제22조 (분쟁의 해결)</h3>
          <ol className="list-decimal ml-5 space-y-1">
            <li>
              ‘회사’는 ‘이용자’가 제기하는 불만사항 및 의견을 지체없이 처리하기
              위하여 노력합니다. 다만 신속한 처리가 곤란한 경우 ‘이용자’에게 그
              사유와 처리일정을 즉시 통보해 드립니다.
            </li>
            <li>
              ‘회사’와 ‘이용자’간 전자상거래에 관한 분쟁이 발생한 경우,
              ‘이용자’는 한국소비자원, 전자문서 • 전자거래 분쟁조정위원회 등
              분쟁조정기관에 조정을 신청할 수 있습니다.
            </li>
            <li>
              ‘회사’와 ‘이용자’간 발생한 분쟁에 관한 소송은 민사소송법에 따른
              관할법원에 제기하며, 준거법은 대한민국의 법령을 적용합니다.
            </li>
          </ol>
        </section>

        <hr className="my-6" />
        <section>
          <h3 className="font-semibold">부 칙</h3>
          <p>제1조(시행일) 본 약관은 2025.11.01.부터 시행합니다.</p>
        </section>
      </div>
    </div>
  );
};

export default TermsOfService;
