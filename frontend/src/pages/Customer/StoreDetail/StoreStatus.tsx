import { CommonBtn } from "@components/common";
import type { ProductBaseType } from "@interface";
import { getRoundedPrice } from "@utils";

interface StoreStatus {
  mainProd: ProductBaseType;
  isStoreOpenWindow: boolean;
  isPickupNotEnded: boolean;
  setOpenCheckNoti: (noti: boolean) => void;
}

export const StoreStatus = ({
  mainProd,
  isStoreOpenWindow,
  isPickupNotEnded,
  setOpenCheckNoti,
}: StoreStatus) => {
  return (
    <div>
      {!(isStoreOpenWindow && isPickupNotEnded) ? (
        <CommonBtn category="grey" label="지금은 구매할 수 없어요" />
      ) : mainProd.current_stock > 0 ? (
        <CommonBtn
          category="green"
          onClick={() => setOpenCheckNoti(true)}
          label={`${getRoundedPrice(
            mainProd.price,
            mainProd.sale
          ).toLocaleString()}원 구매하기 (${mainProd.current_stock}개 남음)`}
        />
      ) : (
        <CommonBtn category="grey" label="품절됐어요" />
      )}
    </div>
  );
};
