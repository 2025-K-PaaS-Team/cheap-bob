import DetailHeader from "@components/customer/storeDetail";

interface CommonDescProps {
  desc: string;
  name: string;
  phone: string;
}

const CommonDesc = ({ desc, name, phone }: CommonDescProps) => {
  const formattedPhone = (phone: string) => {
    if (!phone) return "";
    phone = phone.replace(/\D/g, "");

    // 서울(02) 번호
    if (phone.startsWith("02")) {
      if (phone.length === 9)
        return phone.replace(/(\d{2})(\d{3})(\d{4})/, "$1-$2-$3");
      if (phone.length === 10)
        return phone.replace(/(\d{2})(\d{4})(\d{4})/, "$1-$2-$3");
    }
    // 기타 지역번호 3자리
    else if (phone.length === 10 && /^[0-9]{10}$/.test(phone)) {
      return phone.replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
    } else if (phone.length === 11 && /^[0-9]{11}$/.test(phone)) {
      return phone.replace(/(\d{3})(\d{4})(\d{4})/, "$1-$2-$3");
    }
    // 특수번호 4+4
    else if (phone.length === 8) {
      return phone.replace(/(\d{4})(\d{4})/, "$1-$2");
    }

    return phone; // 포맷 안 맞으면 그냥 리턴
  };

  return (
    <div className="flex flex-col">
      <DetailHeader name={name || ""} />
      <div className="bodyFont top-[80px] px-[20px] h-full w-full inset-0 flex flex-col items-start justify-start z-50">
        <div>{desc || ""}</div>
        <br />
        <div>{formattedPhone(phone) || ""}</div>
      </div>
    </div>
  );
};

export default CommonDesc;
