import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface CommonLoadingProps {
  type?: "default" | "data" | "payment" | "upload" | "login" | "submit";
  isLoading: boolean;
}
const CommonLoading = ({ type = "default", isLoading }: CommonLoadingProps) => {
  const [isVisible, setIsVisible] = useState(true);

  const loadingText: Record<string, string> = {
    default: "잠시만 기다려주세요.",
    data: "데이터를 불러오는 중이에요...",
    payment: "결제를 처리 중이에요...",
    upload: "파일을 업로드하고 있어요...",
    login: "로그인 중이에요...",
    submit: "제출을 완료하는 중이에요...",
  };

  useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => setIsVisible(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 1 }}
      animate={{ opacity: isLoading ? 1 : 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center fixed inset-0 z-[9999]"
    >
      <motion.div
        animate={{
          rotate: 360,
          scale: [1, 1.1, 1],
        }}
        transition={{
          rotate: { duration: 1.5, repeat: Infinity, ease: "linear" },
          scale: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
        }}
      >
        <Loader2 className="w-10 h-10 text-main-deep" />
      </motion.div>

      <motion.div
        className="mt-4 text-custom-black"
        animate={{ opacity: [0.8, 1, 0.8] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        {loadingText[type]}
      </motion.div>
    </motion.div>
  );
};

export default CommonLoading;
