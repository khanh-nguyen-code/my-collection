from typing import List, Tuple, Optional

import torch
from nn_module import Module, CRF
from torch import nn


class CharBiLSTM_WordBiLSTM_CRF(Module):
    """
    CharBiLSTM_WordBiLSTM_CRF :
    """

    def __init__(
            self,
            num_chars: int,
            char_embedding_dim: int,
            char_hidden_dim: int,
            word_external_dim: int,
            word_hidden_dim,
            num_tags: int,
            batch_first: bool = True,
    ):
        """
        :param num_chars: number of characters
        :param char_embedding_dim: embedding dimension for each character
        :param char_hidden_dim: hidden dimension for each char lstm (1 normal, 1 reverse)
        :param word_external_dim: external dimension for word embedding (e.g word2vec, bert)
        :param word_hidden_dim: hidden dimension for each word lstm (1 normal, 1 reverse)
        :param num_tags: number of tags
        :param batch_first:
        """
        super(CharBiLSTM_WordBiLSTM_CRF, self).__init__()
        self.num_chars = num_chars
        self.char_embedding_dim = char_embedding_dim
        self.char_hidden_dim = char_hidden_dim
        self.word_external_dim = word_external_dim
        self.word_embedding_dim = 2 * self.char_hidden_dim + self.word_external_dim
        self.word_hidden_dim = word_hidden_dim
        self.num_tags = num_tags
        self.batch_first = batch_first

        self.char_embedding = nn.Embedding(
            num_embeddings=self.num_chars,
            embedding_dim=self.char_embedding_dim,
        )
        self.char_lstm = nn.LSTM(
            input_size=self.char_embedding_dim,
            hidden_size=self.char_hidden_dim,
            num_layers=1,
            bidirectional=True,
            batch_first=True,
        )
        self.word_lstm = nn.LSTM(
            input_size=self.word_embedding_dim,
            hidden_size=self.word_hidden_dim,
            num_layers=1,
            bidirectional=True,
            batch_first=True,
        )
        self.linear = nn.Linear(
            in_features=2 * self.word_hidden_dim,
            out_features=self.num_tags,
        )
        self.crf = CRF(
            num_tags=num_tags,
            batch_first=True,
        )

    def _random_char_hidden(self, batch_size: int = 1) -> Tuple[torch.Tensor, torch.Tensor]:
        return torch.randn(2, batch_size, self.char_hidden_dim).to(self.device), \
               torch.randn(2, batch_size, self.char_hidden_dim).to(self.device)

    def _random_word_hidden(self, batch_size: int = 1):
        return torch.randn(2, batch_size, self.word_hidden_dim).to(self.device), \
               torch.randn(2, batch_size, self.word_hidden_dim).to(self.device)

    def _emit(self,
              document: List[List[torch.Tensor]],
              external: Optional[List[List[torch.Tensor]]] = None,
              ) -> Tuple[torch.Tensor, List[int]]:
        """
        :param document: a list of sentences.
        each sentence is a list of words.
        each word is a tensor representing its characters
        :param external: a list of sentences,
        each sentences is a list of words,
        each word is a tensor of external word embedding
        """
        # CHAR LSTM
        # create array
        max_word_length = max([len(word) for sentence in document for word in sentence])
        num_words = sum([len(sentence) for sentence in document])
        char_tensor = torch.zeros(size=(num_words, max_word_length), dtype=torch.int64).to(self.device)
        word_length = []
        sentence_length = []
        row = 0
        for sentence in document:
            sentence_length.append(len(sentence))
            for word in sentence:
                char_tensor[row, 0:len(word)] = word
                word_length.append(len(word))
                row += 1
        # char embedding
        char_embedding = self.char_embedding(char_tensor)
        # char lstm
        char_embedding_packed = nn.utils.rnn.pack_padded_sequence(
            char_embedding, word_length, batch_first=True, enforce_sorted=False,
        )
        char_lstm_out_packed, _ = self.char_lstm(char_embedding_packed, self._random_char_hidden(batch_size=num_words))
        char_lstm_out, word_length = nn.utils.rnn.pad_packed_sequence(char_lstm_out_packed, batch_first=True)
        # take last hidden of normal lstm and first hidden of reverse lstm
        char_lstm_out_last = torch.cat(
            [char_lstm_out[:, -1, : self.char_hidden_dim], char_lstm_out[:, 0, self.char_hidden_dim:]], dim=-1,
        )
        # WORD LSTM
        num_sentences = len(document)
        max_sentence_length = max([len(sentence) for sentence in document])
        word_tensor = torch.zeros(
            size=(num_sentences, max_sentence_length, self.word_embedding_dim),
            dtype=torch.float32).to(self.device)

        row = 0
        for s_idx, slenght in enumerate(sentence_length):
            for w_in_s_idx in range(slenght):
                word_tensor[s_idx, w_in_s_idx, 0: char_lstm_out_last.shape[1]] = char_lstm_out_last[row, :]
                row += 1
        # import external word embedding
        if self.word_external_dim > 0 and external is not None:
            for s_idx, sentence in enumerate(external):
                for w_in_s_idx, word in enumerate(sentence):
                    word_tensor[s_idx, w_in_s_idx, 2 * self.char_hidden_dim:] = word
        # word lstm
        word_tensor_packed = nn.utils.rnn.pack_padded_sequence(
            word_tensor, sentence_length, batch_first=True, enforce_sorted=False,
        )
        word_lstm_out_packed, _ = self.word_lstm(word_tensor_packed, self._random_word_hidden(batch_size=num_sentences))
        word_lstm_out, sentence_length = nn.utils.rnn.pad_packed_sequence(word_lstm_out_packed, batch_first=True)

        # linear
        linear_out = self.linear(word_lstm_out)
        return linear_out, sentence_length

    def _length_to_mask(self, lengths: List[int]) -> torch.Tensor:
        max_length = max(lengths)
        batch = len(lengths)
        mask = torch.zeros(size=(batch, max_length), dtype=torch.uint8).to(self.device)
        for idx, length in enumerate(lengths):
            mask[idx, 0:length] = 1
        return mask

    def decode(self,
               document: List[List[torch.Tensor]],
               external: Optional[List[List[torch.Tensor]]] = None,
               ) -> List[List[int]]:
        """
        :param document: a list of sentences.
        each sentence is a list of words.
        each word is a tensor representing its characters
        :param external: a list of sentences,
        each sentences is a list of words,
        each word is a tensor of external word embedding
        :return: predicted tags
        """
        with torch.no_grad():
            linear_out, sentence_length = self._emit(document, external)
            mask = self._length_to_mask(sentence_length)
            # crf
            tags = self.crf.decode(linear_out, mask=mask)
            return tags

    def forward(self,
                document: List[List[torch.Tensor]],
                tags: List[torch.Tensor],
                external: Optional[List[List[torch.Tensor]]] = None,
                ) -> torch.Tensor:
        """
        :param document: a list of sentences.
        each sentence is a list of words.
        each word is a tensor representing its characters
        :param tags: a list of sentences.
        each sentence is a tensor representing tags
        :param external: a list of sentences,
        each sentences is a list of words,
        each word is a tensor of external word embedding
        :return: negative log likelihood
        """
        linear_out, sentence_length = self._emit(document, external)
        mask = self._length_to_mask(sentence_length)
        num_sentences = len(sentence_length)
        max_setence_length = max(sentence_length)
        # tags
        tags_tensor = torch.zeros(size=(num_sentences, max_setence_length), dtype=torch.int64)
        for s_idx, slength in enumerate(sentence_length):
            tags_tensor[s_idx, 0:slength] = tags[s_idx]
        # crf
        crf_nll_out = self.crf(linear_out, tags_tensor, mask=mask, reduction="mean")
        return - crf_nll_out


class BiLSTM_CRF_HeadTail(Module):
    def __init__(
            self,
            num_chars: int,
            char_embedding_dim: int,
            char_hidden_dim: int,
            word_external_dim: int,
            word_hidden_dim,
            num_tags: int,
            batch_first: bool = True,
    ):
        """
        :param num_chars: number of characters
        :param char_embedding_dim: embedding dimension for each character
        :param char_hidden_dim: hidden dimension for each char lstm (1 normal, 1 reverse)
        :param word_external_dim: external dimension for word embedding (e.g word2vec, bert)
        :param word_hidden_dim: hidden dimension for each word lstm (1 normal, 1 reverse)
        :param num_tags: number of tags
        :param batch_first:
        """
        super(BiLSTM_CRF_HeadTail, self).__init__()
        self.num_chars = num_chars
        self.char_embedding_dim = char_embedding_dim
        self.char_hidden_dim = char_hidden_dim
        self.word_external_dim = word_external_dim
        self.word_embedding_dim = 4 * self.char_hidden_dim + self.word_external_dim
        self.word_hidden_dim = word_hidden_dim
        self.num_tags = num_tags
        self.batch_first = batch_first

        self.char_embedding = nn.Embedding(
            num_embeddings=self.num_chars,
            embedding_dim=self.char_embedding_dim,
        )
        self.char_lstm = nn.LSTM(
            input_size=self.char_embedding_dim,
            hidden_size=self.char_hidden_dim,
            num_layers=1,
            bidirectional=True,
            batch_first=True,
        )
        self.word_lstm = nn.LSTM(
            input_size=self.word_embedding_dim,
            hidden_size=self.word_hidden_dim,
            num_layers=1,
            bidirectional=True,
            batch_first=True,
        )
        self.linear = nn.Linear(
            in_features=2 * self.word_hidden_dim,
            out_features=self.num_tags,
        )
        self.crf = CRF(
            num_tags=num_tags,
            batch_first=True,
        )

    def _random_char_hidden(self, batch_size: int = 1) -> Tuple[torch.Tensor, torch.Tensor]:
        return torch.randn(2, batch_size, self.char_hidden_dim).to(self.device), \
               torch.randn(2, batch_size, self.char_hidden_dim).to(self.device)

    def _random_word_hidden(self, batch_size: int = 1):
        return torch.randn(2, batch_size, self.word_hidden_dim).to(self.device), \
               torch.randn(2, batch_size, self.word_hidden_dim).to(self.device)

    def _emit(self,
              document: List[List[torch.Tensor]],
              external: Optional[List[List[torch.Tensor]]] = None,
              ) -> Tuple[torch.Tensor, List[int]]:
        """
        :param document: a list of sentences.
        each sentence is a list of words.
        each word is a tensor representing its characters
        :param external: a list of sentences,
        each sentences is a list of words,
        each word is a tensor of external word embedding
        """
        # CHAR LSTM
        # create array
        max_word_length = max([len(word) for sentence in document for word in sentence])
        num_words = sum([len(sentence) for sentence in document])
        char_tensor = torch.zeros(size=(num_words, max_word_length), dtype=torch.int64).to(self.device)
        word_length = []
        sentence_length = []
        row = 0
        for sentence in document:
            sentence_length.append(len(sentence))
            for word in sentence:
                char_tensor[row, 0:len(word)] = word
                word_length.append(len(word))
                row += 1
        # char embedding
        char_embedding = self.char_embedding(char_tensor)
        # char lstm
        char_embedding_packed = nn.utils.rnn.pack_padded_sequence(
            char_embedding, word_length, batch_first=True, enforce_sorted=False,
        )
        char_lstm_out_packed, _ = self.char_lstm(char_embedding_packed, self._random_char_hidden(batch_size=num_words))
        char_lstm_out, word_length = nn.utils.rnn.pad_packed_sequence(char_lstm_out_packed, batch_first=True)
        # take last hidden of normal lstm and first hidden of reverse lstm
        char_lstm_out_last = torch.cat(
            [char_lstm_out[:, -1, :], char_lstm_out[:, 0, :]], dim=-1,
        )
        # WORD LSTM
        num_sentences = len(document)
        max_sentence_length = max([len(sentence) for sentence in document])
        word_tensor = torch.zeros(
            size=(num_sentences, max_sentence_length, self.word_embedding_dim),
            dtype=torch.float32).to(self.device)

        row = 0
        for s_idx, slenght in enumerate(sentence_length):
            for w_in_s_idx in range(slenght):
                word_tensor[s_idx, w_in_s_idx, 0: char_lstm_out_last.shape[1]] = char_lstm_out_last[row, :]
                row += 1
        # import external word embedding
        if self.word_external_dim > 0 and external is not None:
            for s_idx, sentence in enumerate(external):
                for w_in_s_idx, word in enumerate(sentence):
                    word_tensor[s_idx, w_in_s_idx, 2 * self.char_hidden_dim:] = word
        # word lstm
        word_tensor_packed = nn.utils.rnn.pack_padded_sequence(
            word_tensor, sentence_length, batch_first=True, enforce_sorted=False,
        )
        word_lstm_out_packed, _ = self.word_lstm(word_tensor_packed, self._random_word_hidden(batch_size=num_sentences))
        word_lstm_out, sentence_length = nn.utils.rnn.pad_packed_sequence(word_lstm_out_packed, batch_first=True)

        # linear
        linear_out = self.linear(word_lstm_out)
        return linear_out, sentence_length

    def _length_to_mask(self, lengths: List[int]) -> torch.Tensor:
        max_length = max(lengths)
        batch = len(lengths)
        mask = torch.zeros(size=(batch, max_length), dtype=torch.uint8).to(self.device)
        for idx, length in enumerate(lengths):
            mask[idx, 0:length] = 1
        return mask

    def decode(self,
               document: List[List[torch.Tensor]],
               external: Optional[List[List[torch.Tensor]]] = None,
               ) -> List[List[int]]:
        """
        :param document: a list of sentences.
        each sentence is a list of words.
        each word is a tensor representing its characters
        :param external: a list of sentences,
        each sentences is a list of words,
        each word is a tensor of external word embedding
        :return: predicted tags
        """
        with torch.no_grad():
            linear_out, sentence_length = self._emit(document, external)
            mask = self._length_to_mask(sentence_length)
            # crf
            tags = self.crf.decode(linear_out, mask=mask)
            return tags

    def forward(self,
                document: List[List[torch.Tensor]],
                tags: List[torch.Tensor],
                external: Optional[List[List[torch.Tensor]]] = None,
                ) -> torch.Tensor:
        """
        :param document: a list of sentences.
        each sentence is a list of words.
        each word is a tensor representing its characters
        :param tags: a list of sentences.
        each sentence is a tensor representing tags
        :param external: a list of sentences,
        each sentences is a list of words,
        each word is a tensor of external word embedding
        :return: negative log likelihood
        """
        linear_out, sentence_length = self._emit(document, external)
        mask = self._length_to_mask(sentence_length)
        num_sentences = len(sentence_length)
        max_setence_length = max(sentence_length)
        # tags
        tags_tensor = torch.zeros(size=(num_sentences, max_setence_length), dtype=torch.int64)
        for s_idx, slength in enumerate(sentence_length):
            tags_tensor[s_idx, 0:slength] = tags[s_idx]
        # crf
        crf_nll_out = self.crf(linear_out, tags_tensor, mask=mask, reduction="mean")
        return - crf_nll_out
