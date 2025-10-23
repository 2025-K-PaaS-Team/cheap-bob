interface Layout {
  key: string;
  back: boolean;
  title: string;
  centerIcon?: boolean;
  loc?: boolean;
  heart?: boolean;
  noti?: boolean;
  paths: (string | RegExp)[];
}

export const layoutMap: Layout[] = [
  {
    key: "Home",
    paths: ["/c", "/c/stores"],
    back: false,
    title: "",
    centerIcon: true,
    loc: true,
    heart: true,
    noti: true,
  },
  {
    key: "onBoarding",
    paths: ["/c/signup"],
    back: true,
    title: "",
  },
  {
    key: "Payment",
    paths: [/^\/c\/stores\/.*\/payment$/],
    back: true,
    title: "결제",
  },
  {
    key: "StoreSearch",
    paths: [/^\/c\/stores\/search.*/],
    back: true,
    title: "검색",
  },
  {
    key: "FavStore",
    paths: ["/c/favorite"],
    back: true,
    title: "관심 가게",
  },
  {
    key: "Order",
    paths: ["/c/order"],
    back: true,
    title: "주문 현황",
  },
  {
    key: "OrderAll",
    paths: ["/c/order/all"],
    back: true,
    title: "주문 내역",
  },
  {
    key: "My",
    paths: ["/c/my"],
    back: false,
    title: "마이페이지",
  },
  {
    key: "ChangeInfo",
    paths: ["/c/change/info"],
    back: true,
    title: "프로필 수정",
  },
  {
    key: "ChangeNutrition",
    paths: ["/c/change/nutrition"],
    back: true,
    title: "영양 목표",
  },
  {
    key: "ChangeAllergy",
    paths: ["/c/change/allergy"],
    back: true,
    title: "못먹는 음식",
  },
  {
    key: "ChangeMenu",
    paths: ["/c/change/menu"],
    back: true,
    title: "선호 메뉴",
  },
  {
    key: "ChangeTopping",
    paths: ["/c/change/topping"],
    back: true,
    title: "선호 토핑",
  },
  {
    key: "SetLoc",
    paths: ["/c/location"],
    back: true,
    title: "위치 설정",
  },
  {
    key: "Search",
    paths: ["/c/search"],
    back: true,
    title: "검색",
  },
  {
    key: "Noti",
    paths: ["/c/noti"],
    back: true,
    title: "주문 알림",
  },
  {
    key: "default",
    paths: [/.*/],
    back: false,
    title: "",
  },
] as const;

export const sellerLayoutMap = [
  // 매장 정보 변경
  {
    key: "changeStoreName",
    paths: [/^\/s\/change\/store\/name$/],
    back: true,
    title: "매장 이름 변경",
  },
  {
    key: "changeStoreDesc",
    paths: [/^\/s\/change\/store\/desc$/],
    back: true,
    title: "매장 소개 변경",
  },
  {
    key: "changeStoreNum",
    paths: [/^\/s\/change\/store\/num$/],
    back: true,
    title: "매장 연락처 변경",
  },
  {
    key: "changeStoreAddr",
    paths: [/^\/s\/change\/store\/addr$/],
    back: true,
    title: "매장 주소 변경",
  },
  {
    key: "changeStoreImg",
    paths: [/^\/s\/change\/store\/img$/],
    back: true,
    title: "이미지 등록 및 변경",
  },
  {
    key: "changeStoreInfo",
    paths: [/^\/s\/change\/store/],
    back: true,
    title: "매장 정보 변경",
  },
  // 영업 시간 변경
  {
    key: "changeOperationOpTime",
    paths: [/^\/s\/change\/operation\/op-time$/],
    back: true,
    title: "영업 시간 변경",
  },
  {
    key: "changeOperationPuTime",
    paths: [/^\/s\/change\/operation\/pu-time$/],
    back: true,
    title: "픽업 시간 변경",
  },
  {
    key: "changeOperationInfo",
    paths: [/^\/s\/change\/operation/],
    back: true,
    title: "영업 시간 변경",
  },
  // 패키지 정보 변경
  {
    key: "changePackageName",
    paths: [/^\/s\/change\/package\/name$/],
    back: true,
    title: "패키지 이름 변경",
  },
  {
    key: "changePackageDesc",
    paths: [/^\/s\/change\/package\/desc$/],
    back: true,
    title: "패키지 소개 변경",
  },
  {
    key: "changePackageNutrition",
    paths: [/^\/s\/change\/package\/nutrition$/],
    back: true,
    title: "영양목표 변경",
  },
  {
    key: "changePackagePrice",
    paths: [/^\/s\/change\/package\/price$/],
    back: true,
    title: "패키지 가격 변경",
  },
  {
    key: "changePackageNum",
    paths: [/^\/s\/change\/package\/num$/],
    back: true,
    title: "판매 기본값 변경",
  },
  {
    key: "changePackageInfo",
    paths: [/^\/s\/change\/package/],
    back: true,
    title: "패키지 정보 변경",
  },
  {
    key: "billingHistory",
    paths: ["/s/billing/history"],
    back: true,
    title: "정산 내역 보기",
  },
  {
    key: "billingChange",
    paths: ["/s/billing/change"],
    back: true,
    title: "정산 정보 변경",
  },
  {
    key: "default",
    paths: [/.*/],
    back: false,
    title: "",
  },
] as const;
