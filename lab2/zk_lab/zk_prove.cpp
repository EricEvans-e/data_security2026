#include "common.hpp"

int main(int argc, char *argv[])
{
    try {
        const std::string artifacts_dir = lab2::parse_string_flag(argc, argv, "--artifacts-dir", ".");
        const long long x_value = lab2::parse_long_flag(argc, argv, "--x", 3);
        const long long out_value = lab2::parse_long_flag(argc, argv, "--out", 35);

        const auto witness = lab2::build_witness(x_value);

        lab2::print_statement_banner("Prove", out_value);
        lab2::print_witness_banner(witness);

        if (!lab2::witness_matches_statement(witness, out_value)) {
            std::cerr << "Witness does not satisfy the public statement." << std::endl;
            return EXIT_FAILURE;
        }

        const auto pb = lab2::build_protoboard<lab2::FieldT>(out_value, &witness);
        if (!pb.is_satisfied()) {
            std::cerr << "Constraint system is not satisfied." << std::endl;
            return EXIT_FAILURE;
        }

        const auto pk =
            lab2::load_object<libsnark::r1cs_gg_ppzksnark_proving_key<lab2::ppT> >(
                lab2::artifact_path(artifacts_dir, "pk.raw"));

        const auto proof = libsnark::r1cs_gg_ppzksnark_prover<lab2::ppT>(
            pk,
            pb.primary_input(),
            pb.auxiliary_input());

        lab2::save_object(lab2::artifact_path(artifacts_dir, "proof.raw"), proof);

        std::cout << "Primary input: " << pb.primary_input() << std::endl;
        std::cout << "Auxiliary input: " << pb.auxiliary_input() << std::endl;
        std::cout << "Saved proof to: " << lab2::artifact_path(artifacts_dir, "proof.raw") << std::endl;
        return EXIT_SUCCESS;
    } catch (const std::exception &ex) {
        std::cerr << "[zk_prove] " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }
}
