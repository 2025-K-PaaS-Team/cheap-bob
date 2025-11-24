import { idxToDow } from "@constant";
import type { StoreSearchBaseType } from "@interface";

interface StoreOpTimeType {
  store: StoreSearchBaseType;
}

export const StoreOpTime = ({ store }: StoreOpTimeType) => {
  return (
    <div className="gap-y-[13px] flex flex-col">
      <h3>영업 시간</h3>
      <div className="tagFont">
        {store.operation_times
          .filter((dow) => dow.is_open_enabled === true)
          .sort((a, b) => a.day_of_week - b.day_of_week)
          .map((dow) => (
            <div key={dow.day_of_week}>
              {idxToDow[dow.day_of_week]} {dow.open_time.slice(0, 5)} ~{" "}
              {dow.close_time.slice(0, 5)}
            </div>
          ))}
      </div>
    </div>
  );
};
