import DetailHeader from "@components/customer/storeDetail";

interface CommonDescProps {
  desc: string;
  name: string;
}

const CommonDesc = ({ desc, name }: CommonDescProps) => {
  return (
    <div className="flex flex-col">
      <DetailHeader name={name || ""} />
      <div className="absolute top-[60px] inset-0 flex items-center justify-center z-50">
        <div className="bodyFont h-full w-full px-[20px] pt-[37px] bg-white">
          {desc || ""}
        </div>
      </div>
    </div>
  );
};

export default CommonDesc;
