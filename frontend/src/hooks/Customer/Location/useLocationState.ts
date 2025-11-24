import { SIDO_KEY, SIGUNGU_KEY, DONGS_KEY } from "@constant";
import { useEffect, useState } from "react";

export const useLocationState = () => {
  const [selectedSiDo, setSelectedSiDo] = useState<string | null>(null);
  const [selectedSiGunGu, setSelectedSiGunGu] = useState<string | null>(null);
  const [selectedDongs, setSelectedDongs] = useState<Record<string, boolean>>(
    {}
  );
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const siDo = localStorage.getItem(SIDO_KEY);
    const siGunGu = localStorage.getItem(SIGUNGU_KEY);
    const dongs = localStorage.getItem(DONGS_KEY);

    if (siDo) setSelectedSiDo(siDo);
    if (siGunGu) setSelectedSiGunGu(siGunGu);
    if (dongs) setSelectedDongs(JSON.parse(dongs));

    setIsLoading(false);
  }, []);

  return {
    selectedSiDo,
    setSelectedSiDo,
    selectedSiGunGu,
    setSelectedSiGunGu,
    selectedDongs,
    setSelectedDongs,
    isLoading,
  };
};
