export const StoreNotice = () => {
    return (
      <div className="gap-y-[13px] flex flex-col">
        <h3>주문 후 약속</h3>
        <div className="hintFont">
          <ol className="list-decimal bg-custom-white py-[18px] px-[15px] rounded">
            <li className="ml-4">
              오직 픽업 시간에만 가게에서 픽업할 수 있어요.
            </li>
            <li className="ml-4">사장님께 따로 메뉴 요청을 할 수 없어요.</li>
            <li className="ml-4">
              픽업 확정 전, 가게 사정에 의해 취소될 수 있어요.
            </li>
            <li className="ml-4">취소사유는 구매 내역에서 확인할 수 있어요.</li>
            <li className="ml-4">
              주문 취소는 가게의 픽업 확정 이후에는 불가능해요.
            </li>
          </ol>
        </div>
      </div>
    );
}