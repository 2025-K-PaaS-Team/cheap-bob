import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface CommonLoadingProps {
  type?: "default" | "data" | "payment" | "upload" | "login" | "submit";
}
const CommonLoading = ({ type = "default" }: CommonLoadingProps) => {
  const loadingText: Record<string, string> = {
    default: "잠시만 기다려주세요.",
    data: "데이터를 불러오는 중이에요...",
    payment: "결제를 처리 중이에요...",
    upload: "파일을 업로드하고 있어요...",
    login: "로그인 중이에요...",
    submit: "제출을 완료하는 중이에요...",
  };

  return (
    <div className="flex flex-col items-center justify-center fixed inset-0 bg-white/50 backdrop-blur-sm z-[9999]">
      <motion.div
        initial={{ rotate: 0, scale: 0.8, opacity: 1 }}
        animate={{ rotate: 360, scale: [1, 1.1, 1], opacity: 1 }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
      >
        <Loader2 className="w-10 h-10 text-main-deep" />
      </motion.div>

      <motion.div
        className="mt-4 text-custom-black"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0.8, 1, 0.8] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        {loadingText[type]}
      </motion.div>
    </div>
  );
};

export default CommonLoading;
