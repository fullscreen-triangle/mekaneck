import { motion } from "framer-motion";
import Link from "next/link";

let MotionLink = motion(Link);

const Logo = () => {
  return (
    <div className="flex flex-col items-center justify-center mt-2">
      <MotionLink
        href="/"
        className="flex items-center justify-center rounded-full w-12 h-12 bg-primary text-white
        text-sm font-bold tracking-tight border-2 border-primary/50"
        whileHover={{
          scale: 1.05,
          boxShadow: "0 0 25px rgba(99,102,241,0.4)",
        }}
        whileTap={{ scale: 0.95 }}
      >
        NPL
      </MotionLink>
    </div>
  );
};

export default Logo;
