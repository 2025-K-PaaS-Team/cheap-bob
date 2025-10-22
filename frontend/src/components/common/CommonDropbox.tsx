import type { OptionType } from "@interface/common/types";
import Select, { type SingleValue } from "react-select";

interface CommonDropboxProps {
  options: OptionType[];
  value: OptionType | null;
  onChange: (options: OptionType | null) => void;
  placeholder: string;
}

const CommonDropbox = ({
  options,
  value,
  onChange,
  placeholder,
}: CommonDropboxProps) => {
  return (
    <div>
      <Select
        isSearchable={false}
        value={value}
        onChange={(newValue: SingleValue<OptionType>) => onChange(newValue)}
        options={options}
        placeholder={placeholder}
      />
    </div>
  );
};

export default CommonDropbox;
