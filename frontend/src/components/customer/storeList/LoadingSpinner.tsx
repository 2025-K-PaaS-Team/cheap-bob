import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export const LoadingSpinner = () => (
  <motion.div
    animate={{ rotate: 360, scale: [1, 1.1, 1] }}
    transition={{
      rotate: { duration: 1.5, repeat: Infinity, ease: "linear" },
      scale: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
    }}
  >
    <Loader2 className="w-7 h-7 text-main-deep" />
  </motion.div>
);
