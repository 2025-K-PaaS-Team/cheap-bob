import type { OptionType } from "@interface/common/types";
import Select, { type SingleValue } from "react-select";

interface CommonDropboxProps {
  options: OptionType[];
  value: OptionType | null;
  onChange: (options: OptionType | null) => void;
}

const CommonDropbox = ({ options, value, onChange }: CommonDropboxProps) => {
  return (
    <div>
      <Select
        isSearchable={false}
        value={value}
        onChange={(newValue: SingleValue<OptionType>) => onChange(newValue)}
        options={options}
        placeholder="변경할 영업 상태를 선택해 주세요."
      />
    </div>
  );
};

export default CommonDropbox;
