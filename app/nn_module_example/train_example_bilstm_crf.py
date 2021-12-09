import random
from typing import List, Tuple, Iterator

import torch
from my_collection.nn_module import CharBiLSTM_WordBiLSTM_CRF
from torch import optim


def train(
        document: List[List[List[int]]],
        tags: List[List[int]],
        num_chars: int,
        num_tags: int,
        char_embedding_dim: int = 4,
        char_hidden_dim: int = 8,
        word_hidden_dim: int = 16,
        num_epochs: int = 250,
):
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
    else:
        device = torch.device("cpu")

    # PREPARE DATASET
    def data_in() -> Iterator[Tuple[List[List[torch.Tensor]], List[torch.Tensor]]]:
        document_in = [[torch.tensor(word, dtype=torch.int64).to(device) for word in sentence] for sentence in document]
        tags_in = [torch.tensor(sentence, dtype=torch.int64).to(device) for sentence in tags]
        for _ in range(num_epochs):
            yield document_in, tags_in

    # MODEL
    model = CharBiLSTM_WordBiLSTM_CRF(
        num_chars=num_chars,
        char_embedding_dim=char_embedding_dim,
        char_hidden_dim=char_hidden_dim,
        word_external_dim=0,
        word_hidden_dim=word_hidden_dim,
        num_tags=num_tags,
        batch_first=True,
    )

    def report(title: str = ""):
        model.eval()
        document_in, tags_in = next(iter(data_in()))
        loss = model.forward(document=document_in, tags=tags_in)
        print(f"{title}")
        print(f"nll loss: \t{float(loss.detach().cpu().numpy())}")
        print(f"actual: \t{tags}")
        print(f"pred  : \t{model.decode(document=document_in)}")
        print()

    report("epoch 0")
    # TRAIN
    mark = num_epochs // 10
    optimizer = optim.SGD(model.parameters(), lr=0.1, weight_decay=1e-4)
    for epoch, (document_in, tags_in) in enumerate(data_in()):
        model.train()
        model.zero_grad()
        loss = model.forward(document=document_in, tags=tags_in)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % mark == 0:
            report(f"epoch {epoch + 1}")

    report("epoch last")


if __name__ == "__main__":
    document = [
        "the wall street journal reported today that apple corporation made money".split(" "),
        "georgia tech is a university in georgia".split(" "),
    ]
    tags = [
        "B I I I O O O B I O O".split(" "),
        "B I O O O O B".split(" "),
    ]
    # PREPARE DATA
    idx2char = list("abcdefghijklmnopqrstuvwxyz")
    char2idx = {char: idx for idx, char in enumerate(idx2char)}
    idx2tag = ["B", "I", "O"]
    tag2idx = {tag: idx for idx, tag in enumerate(idx2tag)}

    document_in = [[[char2idx[char] for char in word] for word in sentence] for sentence in document]
    tags_in = [[tag2idx[tag] for tag in sentence] for sentence in tags]

    # TRAIN
    random.seed(1234)
    torch.manual_seed(4321)
    train(
        document=document_in,
        tags=tags_in,
        num_chars=len(idx2char),
        num_tags=len(idx2tag),
    )
