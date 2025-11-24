import type { ProductType, StoreSearchBaseType } from "@interface";

interface StoreIntroType {
  store: StoreSearchBaseType;
  product: ProductType;
  handleUpdateFavorStore: (id: string, now: boolean) => void;
  handleClickDirection: () => void;
  isFavor: boolean;
}

export const StoreIntro = ({
  store,
  product,
  handleUpdateFavorStore,
  handleClickDirection,
  isFavor,
}: StoreIntroType) => {
  return (
    <div>
      {/* store name */}
      <h1 className="mr-10">{product.store_name}</h1>

      {/* favor */}
      <div
        className="rounded-full absolute top-1 right-1 z-10 w-[41px] h-[41px] flex justify-center items-center cursor-pointer"
        onClick={() => handleUpdateFavorStore(product.store_id, isFavor)}
      >
        {isFavor ? (
          <img
            src="/icon/heartFull.svg"
            alt="FavoriteStore"
            className="w-5 h-5"
          />
        ) : (
          <img src="/icon/heart.svg" alt="FavoriteStore" className="w-5 h-5" />
        )}
      </div>

      {/* store logo and map */}
      <div className="flex flex-row gap-x-3 mt-[8px]">
        <img
          src="/icon/direction.svg"
          alt="directionIcon"
          onClick={handleClickDirection}
          width={22}
          className="cursor-pointer"
        />

        {store.sns.instagram && (
          <img
            src="/icon/instagram.svg"
            alt="instagramIcon"
            onClick={() => window.open(store.sns.instagram, "_blank")}
            width={22}
            className="cursor-pointer"
          />
        )}
        {store.sns.homepage && (
          <img
            src="/icon/homeFull.svg"
            alt="homeIcon"
            onClick={() => window.open(store.sns.homepage, "_blank")}
            width={22}
            className="cursor-pointer"
          />
        )}
        {store.sns.x && (
          <img
            src="/icon/twitter.svg"
            alt="twitterIcon"
            onClick={() => window.open(store.sns.x, "_blank")}
            width={22}
            className="cursor-pointer"
          />
        )}
      </div>
    </div>
  );
};
