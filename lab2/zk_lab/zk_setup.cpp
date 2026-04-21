#include "common.hpp"

int main(int argc, char *argv[])
{
    try {
        const std::string artifacts_dir = lab2::parse_string_flag(argc, argv, "--artifacts-dir", ".");
        const long long out_value = lab2::parse_long_flag(argc, argv, "--out", 35);

        lab2::print_statement_banner("Setup", out_value);

        const auto pb = lab2::build_protoboard<lab2::FieldT>(out_value, nullptr);
        const auto constraint_system = pb.get_constraint_system();

        const auto keypair =
            libsnark::r1cs_gg_ppzksnark_generator<lab2::ppT>(constraint_system);

        lab2::save_object(lab2::artifact_path(artifacts_dir, "pk.raw"), keypair.pk);
        lab2::save_object(lab2::artifact_path(artifacts_dir, "vk.raw"), keypair.vk);

        std::cout << "Constraint count: " << constraint_system.num_constraints() << std::endl;
        std::cout << "Public input size: " << pb.primary_input().size() << std::endl;
        std::cout << "Saved proving key to: " << lab2::artifact_path(artifacts_dir, "pk.raw") << std::endl;
        std::cout << "Saved verification key to: " << lab2::artifact_path(artifacts_dir, "vk.raw") << std::endl;
        return EXIT_SUCCESS;
    } catch (const std::exception &ex) {
        std::cerr << "[zk_setup] " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }
}
