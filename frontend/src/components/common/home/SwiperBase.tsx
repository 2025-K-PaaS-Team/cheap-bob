type SwiperBaseProps = {
  title: string;
  img: string;
};

const SwiperBase = ({ title, img }: SwiperBaseProps) => {
  return (
    <div className="flex flex-col items-center font-bold text-2xl">
      <div className="w-fit text-center mb-[31px]">
        {title.split("\n").map((line, idx) => (
          <p key={idx}>{line}</p>
        ))}
      </div>
      <img src={img} alt="phoneMockUp" className="mb-[24px]" />
    </div>
  );
};

export default SwiperBase;
