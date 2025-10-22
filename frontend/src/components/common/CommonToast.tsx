import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import ReactDOM from "react-dom";

interface CommonToastProps {
  type: "success" | "error";
  message: string;
}
const CommonToast = ({ type, message }: CommonToastProps) => {
  const [visible, setVisible] = useState(true);

  const portalTarget = useMemo(() => {
    return (
      (document.querySelector("#toast-root") as HTMLElement) ?? document.body
    );
  }, []);

  useEffect(() => {
    if (!portalTarget) return;

    const timer = setTimeout(() => setVisible(false), 2500);

    return () => {
      clearTimeout(timer);
    };
  }, [portalTarget]);

  return ReactDOM.createPortal(
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.5 }}
          className="absolute w-[90%] bottom-[30px] left-1/2 -translate-x-1/2 p-5 z-[1000] flex items-center bg-[#0a0a0a]/60 rounded-md bodyFont text-white gap-x-[20px]"
        >
          {type === "success" ? (
            <img src="/icon/toastGreen.svg" alt="greenToast" />
          ) : (
            <img src="/icon/toastRed.svg" alt="redToast" />
          )}
          <div dangerouslySetInnerHTML={{ __html: message }} />
        </motion.div>
      )}
    </AnimatePresence>,
    portalTarget
  );
};

export default CommonToast;
