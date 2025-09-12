import {
  CrateNutrition,
  CreateAllergies,
  CreatePreferMenu,
  DeleteAllergies,
  DeleteNutrition,
  DeletePreferMenu,
  GetAllergies,
  GetNutrition,
  GetPreferMenu,
  UpdateCustomerDetail,
} from "@services";

const SignupLab = () => {
  const handleUpdateCustomerDetail = async () => {
    try {
      const res = await UpdateCustomerDetail({
        nickname: "Logitex",
        phone_number: "01099998888",
      });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleGetPreferMenu = async () => {
    try {
      const res = await GetPreferMenu();
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleCreatePreferMenu = async () => {
    try {
      const res = await CreatePreferMenu({ menu_types: ["salad"] });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleDeletePreferMenu = async () => {
    try {
      const res = await DeletePreferMenu({ menu_type: "salad" });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  // nutritions
  const handleGetNutrition = async () => {
    try {
      const res = await GetNutrition();
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleCreateNutrition = async () => {
    try {
      const res = await CrateNutrition({ nutrition_types: ["diet"] });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleDeleteNutrition = async () => {
    try {
      const res = await DeleteNutrition({ nutrition_type: "diet" });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  //   allergies
  const handleGetAllergies = async () => {
    try {
      const res = await GetAllergies();
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleCreateAllergies = async () => {
    try {
      const res = await CreateAllergies({ allergy_types: ["seafood"] });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  const handleDeleteAllergies = async () => {
    try {
      const res = await DeleteAllergies({ allergy_type: "seafood" });
    } catch (err: unknown) {
      console.error("fail", err);
    }
  };

  return (
    <div className="m-3 gap-y-3 flex flex-col">
      <button
        onClick={handleUpdateCustomerDetail}
        className="bg-yellow-200 p-3"
      >
        UpdateCustomerDetail
      </button>

      <button onClick={handleGetPreferMenu} className="bg-yellow-200 p-3">
        GetPreferMenu
      </button>

      <button onClick={handleCreatePreferMenu} className="bg-yellow-200 p-3">
        CreatePreferMenu
      </button>

      <button onClick={handleDeletePreferMenu} className="bg-yellow-200 p-3">
        DeletePreferMenu
      </button>

      {/* nutrition */}
      <button onClick={handleGetNutrition} className="bg-yellow-300 p-3">
        GetNutrition
      </button>

      <button onClick={handleCreateNutrition} className="bg-yellow-300 p-3">
        CrateNutrition
      </button>

      <button onClick={handleDeleteNutrition} className="bg-yellow-300 p-3">
        DeleteNutrition
      </button>

      {/* allergies */}
      <button onClick={handleGetAllergies} className="bg-yellow-400 p-3">
        GetAllergies
      </button>

      <button onClick={handleCreateAllergies} className="bg-yellow-400 p-3">
        CreateAllergies
      </button>

      <button onClick={handleDeleteAllergies} className="bg-yellow-400 p-3">
        DeleteAllergies
      </button>
    </div>
  );
};

export default SignupLab;
