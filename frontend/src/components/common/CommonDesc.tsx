interface CommonDescProps {
  desc: string;
}

const CommonDesc = ({ desc }: CommonDescProps) => {
  return (
    <div className="fixed top-[60px] inset-0 flex items-center justify-center z-50">
      <div className="bodyFont h-full w-full px-[20px] pt-[37px] bg-white">
        {desc}
      </div>
    </div>
  );
};

export default CommonDesc;
