// zerog_helper.js

import { NHFile, NHProvider, getFlowContract } from 'zerog-da-sdk';
import { ethers } from 'ethers';

async function upload_file(file_path, rpc_url, flow_contract_address, private_key, tag_bytes) {
    const file = await NHFile.fromFilePath(file_path);
    const nhProvider = new NHProvider(rpc_url);
    await nhProvider.uploadFile(file);

    const provider = new ethers.providers.JsonRpcProvider(rpc_url);
    const signer = new ethers.Wallet(private_key, provider);
    const flowContract = getFlowContract(flow_contract_address, signer);

    const [submission, err] = await file.createSubmission(tag_bytes);
    if (err != null) {
        console.log('create submission error: ', err);
        return;
    }

    let tx = await flowContract.submit(submission);
    await tx.wait();
    console.log(tx.hash);
}

module.exports = {
    upload_file
};
