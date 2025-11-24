import { useEffect, useRef } from "react";

export const useInfiniteScroll = (
  callback: () => void,
  shouldLoad: boolean
) => {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && shouldLoad) {
          callback();
        }
      },
      { threshold: 0.1, rootMargin: "0px 0px 100px 0px" }
    );

    const el = sentinelRef.current;
    if (el) observer.observe(el);
    return () => {
      if (el) observer.unobserve(el);
    };
  }, [callback, shouldLoad]);

  return sentinelRef;
};
