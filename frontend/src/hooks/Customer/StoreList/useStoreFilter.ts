import { useState, useEffect, useMemo } from "react";
import { GetPreferMenu } from "@services";
import type { PreferMenuBaseType, StoreSearchType } from "@interface";

export const useStoreFilter = (stores: StoreSearchType | undefined) => {
  const [selected, setSelected] = useState<Record<string, boolean>>({
    all: true,
  });
  const [isPreferLoaded, setIsPreferLoaded] = useState(false);

  useEffect(() => {
    const loadPreferredMenus = async () => {
      try {
        const localSelectedStr = localStorage.getItem("preferredMenus");
        if (localSelectedStr) {
          setSelected(JSON.parse(localSelectedStr));
        } else {
          const res = await GetPreferMenu();
          const selectedFromApi: Record<string, boolean> = { all: false };
          res.preferred_menus.forEach((menu: PreferMenuBaseType) => {
            selectedFromApi[menu.menu_type] = true;
          });

          if (Object.keys(selectedFromApi).length === 1) {
            selectedFromApi.all = true;
          }
          setSelected(selectedFromApi);
        }
      } catch {
        setSelected({ all: true });
      } finally {
        setIsPreferLoaded(true);
      }
    };
    loadPreferredMenus();
  }, []);

  useEffect(() => {
    if (isPreferLoaded) {
      localStorage.setItem("preferredMenus", JSON.stringify(selected));
    }
  }, [selected, isPreferLoaded]);

  const filteredStores = useMemo(() => {
    if (!stores) return [];

    const activeKeys = Object.keys(selected).filter(
      (k) => k !== "all" && selected[k]
    );
    const showAll = selected.all || activeKeys.length === 0;

    if (showAll) return stores.stores;

    return stores.stores.filter((store) =>
      store.products.some((p) =>
        p.nutrition_types.some((type) => activeKeys.includes(type))
      )
    );
  }, [stores, selected]);

  return {
    selected,
    setSelected,
    filteredStores,
  };
};
