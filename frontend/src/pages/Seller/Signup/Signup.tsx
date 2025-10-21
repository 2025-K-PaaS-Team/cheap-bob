import { ProgressBar } from "@components/seller/signup";
import { pages, notProgressBarPages, pkgPages } from "@constant";
import type {
  PageComponent,
  ProductRequestType,
  SellerSignupPkgProps,
  SellerSignupProps,
} from "@interface";
import { useState, type JSX } from "react";

const Signup = () => {
  const [pageIdx, setPageIdx] = useState<number>(0);
  const CurrentPage = pages[pageIdx];
  const isProgressBar = !notProgressBarPages.includes(CurrentPage);
  const [pkg, setPkg] = useState<ProductRequestType>({
    product_name: "",
    description: "",
    price: 0,
    sale: 0,
    initial_stock: 0,
    nutrition_types: [],
  });

  const baseProps: SellerSignupProps = { pageIdx, setPageIdx };
  const pkgProps: SellerSignupPkgProps = { ...baseProps, pkg, setPkg };

  // type guard
  const isPkgPage = (
    component: PageComponent
  ): component is (props: SellerSignupPkgProps) => JSX.Element => {
    return pkgPages.includes(component);
  };

  let RenderComponent: JSX.Element;
  if (isPkgPage(CurrentPage)) {
    RenderComponent = <CurrentPage {...pkgProps} />;
  } else {
    const Component = CurrentPage as (props: SellerSignupProps) => JSX.Element;
    RenderComponent = <Component {...baseProps} />;
  }

  return (
    <div className="h-full flex flex-col">
      {isProgressBar && <ProgressBar pageIdx={pageIdx} />}
      <div className="flex flex-1">{RenderComponent}</div>
    </div>
  );
};

export default Signup;
