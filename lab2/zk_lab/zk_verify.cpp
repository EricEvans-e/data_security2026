#include "common.hpp"

int main(int argc, char *argv[])
{
    try {
        const std::string artifacts_dir = lab2::parse_string_flag(argc, argv, "--artifacts-dir", ".");
        const long long out_value = lab2::parse_long_flag(argc, argv, "--out", 35);

        lab2::print_statement_banner("Verify", out_value);

        const auto pb = lab2::build_protoboard<lab2::FieldT>(out_value, nullptr);
        const auto vk =
            lab2::load_object<libsnark::r1cs_gg_ppzksnark_verification_key<lab2::ppT> >(
                lab2::artifact_path(artifacts_dir, "vk.raw"));
        const auto proof =
            lab2::load_object<libsnark::r1cs_gg_ppzksnark_proof<lab2::ppT> >(
                lab2::artifact_path(artifacts_dir, "proof.raw"));

        const bool verified = libsnark::r1cs_gg_ppzksnark_verifier_strong_IC<lab2::ppT>(
            vk,
            pb.primary_input(),
            proof);

        std::cout << "Verification result: " << (verified ? 1 : 0) << std::endl;
        return verified ? EXIT_SUCCESS : EXIT_FAILURE;
    } catch (const std::exception &ex) {
        std::cerr << "[zk_verify] " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }
}
