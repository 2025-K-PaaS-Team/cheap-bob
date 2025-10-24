import { ProgressBar } from "@components/seller/signup";
import { pages, notProgressBarPages, pkgPages } from "@constant";
import type {
  PageComponent,
  ProductRequestType,
  SellerSignupPkgProps,
} from "@interface";
import { useState, type JSX } from "react";
import { useParams } from "react-router-dom";

const Signup = () => {
  const { pageIdx: paramPageIdx } = useParams<{ pageIdx?: string }>();
  const initialPageIdx = Number(paramPageIdx) || 0;
  const CurrentPage = pages[initialPageIdx];
  const isProgressBar = !notProgressBarPages.includes(CurrentPage);
  const [pkg, setPkg] = useState<ProductRequestType>({
    product_name: "",
    description: "",
    price: 0,
    sale: 0,
    initial_stock: 0,
    nutrition_types: [],
  });

  const pkgProps: SellerSignupPkgProps = { pkg, setPkg };

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
    const Component = CurrentPage as () => JSX.Element;
    RenderComponent = <Component />;
  }

  return (
    <div className="h-full flex flex-col">
      {isProgressBar && <ProgressBar />}
      <div className="flex flex-1">{RenderComponent}</div>
    </div>
  );
};

export default Signup;
