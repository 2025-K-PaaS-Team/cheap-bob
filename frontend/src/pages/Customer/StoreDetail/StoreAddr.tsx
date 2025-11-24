import type { StoreSearchBaseType } from "@interface";

interface StoreAddrType {
  store: StoreSearchBaseType;
}

export const StoreAddr = ({ store }: StoreAddrType) => {
  return (
    <div className="gap-y-[13px] flex flex-col">
      <h3>가게 주소</h3>
      <div className="bodyFont">
        {store.address.address} {store.address.detail_address},{" "}
        {store.address.postal_code}
      </div>
    </div>
  );
};
