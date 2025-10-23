type HomeSwiperProps = {
  title: string;
  img: string;
};

const HomeSwiper = ({ title, img }: HomeSwiperProps) => {
  return (
    <h1 className="flex flex-col items-center">
      <div className="text-center">
        {title.split("\n").map((line, idx) => (
          <p key={idx}>{line}</p>
        ))}
      </div>
      <img src={img} alt="phoneMockUp" className="my-[50px] w-1/2" />
    </h1>
  );
};

export default HomeSwiper;
