type HomeSwiperProps = {
  title: string;
  img: string;
};

const HomeSwiper = ({ title, img }: HomeSwiperProps) => {
  return (
    <div className="flex flex-col items-center font-bold text-2xl">
      <div className="text-center mb-[31px]">
        {title.split("\n").map((line, idx) => (
          <p key={idx}>{line}</p>
        ))}
      </div>
      <img src={img} alt="phoneMockUp" className="mb-[30px]" />
    </div>
  );
};

export default HomeSwiper;
