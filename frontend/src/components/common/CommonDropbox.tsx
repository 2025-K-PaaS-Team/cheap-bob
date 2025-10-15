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
        value={value}
        onChange={(newValue: SingleValue<OptionType>) => onChange(newValue)}
        options={options}
      />
    </div>
  );
};

export default CommonDropbox;
